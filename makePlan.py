#!/usr/bin/env python

"""
Usage:
  makePlan.py [-g] [-n <agent_count>] [-s <extra_samples>] <input_file>
  makePlan.py -h | --help

Description:
  Create an optimal (maybe) plan for hyperfielding portals.

  input_file:
      One of two types of files:

      - semi-colon delimited file formatted as portal name; link; (optional) keys

          link is the portal link from the Intel map
          keys is the number of keys you have for the portal

      - .pkl an output from a previous run of this program

          this can be used to make the same plan with a different number of agents

Options:
  -h --help         Show this screen.
  -g                Make maps hideous instead of blue
  -n agents         Number of agents [default: 1]
  -s extra_samples  Number of iterations to run optimization [default: 100]
"""

import os
import errno
import docopt
import pickle
import datetime
import urlparse
import unicodecsv

import networkx as nx
import matplotlib.pyplot as plt

from ftfy import guess_bytes
from lib import maxfield, PlanPrinterMap, geometry, agentOrder
from lib.PlanPrinterMap import GREEN, BLUE

def debug(x): # halfassed debugging thing. remove in final version
    import pprint
    pprint.pprint(x)
    exit()

def main():
    args = docopt.docopt(__doc__)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    COLOR = GREEN if args['-g'] else BLUE


    nagents = int(args['-n'])
    if nagents <= 0:
        print 'Number of agents should be positive'
        exit()


    # We will take many samples in an attempt to reduce number of keys to farm
    # This is the number of samples to take since the last improvement
    EXTRA_SAMPLES = int(args['-s'])
    if EXTRA_SAMPLES not in range(1, 101):
        print 'Number of extra samples must be between 1 and 100'
        exit()


    input_file = args['<input_file>']
    name, ext = os.path.splitext(os.path.basename(input_file))

    try:
        os.makedirs(name)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    output_directory = name + os.sep
    output_file = name + '_' + timestamp + '.pkl'


    if ext != 'pkl':
        a = nx.DiGraph()
        np = geometry.np

        locs = []

        # each line should be name,intel_link,keys
        with open(input_file) as fin:
            text, encoding = guess_bytes(fin.read())
            rows = unicodecsv.reader(text.encode('utf-8').strip().split('\n'), encoding='utf-8')
            for i, row in enumerate(rows):
                a.add_node(i)
                a.node[i]['name'] = row[0]

                url = ','.join(row[1:4]).strip()
                if not url.startswith('http'):
                    print 'Unable to parse input file. Did you forget to put quotes around a name containing a comma?'
                    exit()

                coords = urlparse.parse_qs(urlparse.urlparse(url).query)['pll'][0] # this could have been done the quick and dirty way, but I chose this way. It just felt right
                coord_parts = coords.split(',')
                lat = int(float(coord_parts[0]) * 1.e6)
                lon = int(float(coord_parts[1]) * 1.e6)
                locs.append(np.array([lat, lon], dtype=int)) # why does this have to be a numpy array?
                
                if '.' in row[-1]:
                    a.node[i]['keys'] = 0
                else:
                    a.node[i]['keys'] = int(row[-1])

        n = a.order() # number of nodes
        if n > 65:
            print 'Limit of 65 portals may be optimized at once'
            exit()

        locs = np.array(locs, dtype=float)

        # This part assumes we're working with E6 latitude-longitude data
        locs = geometry.e6LLtoRads(locs)
        xyz  = geometry.radstoxyz(locs)
        xy   = geometry.gnomonicProj(locs,xyz)

        for i in xrange(n):
            a.node[i]['geo'] = locs[i]
            a.node[i]['xyz'] = xyz [i]
            a.node[i]['xy' ] = xy  [i]

        # EXTRA_SAMPLES attempts to get graph with few missing keys
        # Try to minimuze TK + 2*MK where
        #   TK is the total number of missing keys
        #   MK is the maximum number of missing keys for any single portal
        bestgraph = None
        bestlack = np.inf
        bestTK = np.inf
        bestMK = np.inf

        allTK = []
        allMK = []
        allWeights = []

        sinceImprove = 0

        while sinceImprove < EXTRA_SAMPLES:
            b = a.copy()

            sinceImprove += 1

            if not maxfield.maxFields(b):
                print 'Randomization failure\n\tThe program may work if you try again. It is more likely to work if you remove some portals.'
                continue

            TK = 0
            MK = 0
            for j in xrange(n):
                keylack = max(b.in_degree(j)-b.node[j]['keys'],0)
                TK += keylack
                if keylack > MK:
                    MK = keylack

            weightedlack = TK+2*MK

            allTK.append(TK)
            allMK.append(MK)
            allWeights.append(weightedlack)

            if weightedlack < bestlack:
                sinceImprove = 0
                print 'IMPROVEMENT:\ttotal: {}\tmax: {}\tweighted: {}\t{} tries since improvement'.format(TK, MK, weightedlack, sinceImprove)
                bestgraph = b
                bestlack = weightedlack
                bestTK  = TK
                bestMK  = MK
            else:
                print 'this time:\ttotal: {}\tmax: {}\tweighted: {}\t{} tries since improvement'.format(TK, MK, weightedlack, sinceImprove)

            if weightedlack <= 0:
                print 'KEY PERFECTION'
                bestlack = weightedlack
                bestTK  = TK
                bestMK  = MK
                break
            # if num agent keys is zero, this code isn't true...
            # if all([ b.node[i]['keys'] <= b.out_degree(i) for i in xrange(n) ]):
            #     print 'All keys used. Improvement impossible'
            #     break

        if bestgraph == None:
            print 'EXITING RANDOMIZATION LOOP WITHOUT SOLUTION!'
            print ''
            exit()

        print 'Choosing plan requiring {} additional keys, max of {} from single portal'.format(bestTK, bestMK)

        plt.clf()
        plt.scatter(allTK,allMK,c=allWeights,marker='o')
        plt.xlim(min(allTK)-1,max(allTK)+1)
        plt.ylim(min(allMK)-1,max(allMK)+1)
        plt.xlabel('Total keys required')
        plt.ylabel('Max keys required for a single portal')
        cbar = plt.colorbar()
        cbar.set_label('Optimization Weighting (lower=better)')
        plt.savefig(output_directory+'optimization.png')

        a = bestgraph # remember: a = nx.DiGraph()

        # Attach to each edge a list of fields that it completes
        for t in a.triangulation:
            t.markEdgesWithFields()

        agentOrder.improveEdgeOrder(a)

        with open(output_directory+output_file,'w') as fout:
            pickle.dump(a, fout)
    else:
        with open(input_file,'r') as fin:
            a = pickle.load(fin)

    #    agentOrder.improveEdgeOrder(a)
    #    with open(output_directory+output_file,'w') as fout:
    #        pickle.dump(a,fout)

    PP = PlanPrinterMap.PlanPrinter(a, output_directory, nagents, COLOR)
    PP.keyPrep()
    PP.agentKeys()
    PP.planMap()
    PP.agentLinks()

    # These make step-by-step instructional images
    PP.animate()
    PP.split3instruct()

    print "Number of portals: {0}".format(PP.num_portals)
    print "Number of links: {0}".format(PP.num_links)
    print "Number of fields: {0}".format(PP.num_fields)
    portal_ap = (125*8 + 500 + 250)*PP.num_portals
    link_ap = 313 * PP.num_links
    field_ap = 1250 * PP.num_fields
    print "AP from portals capture: {0}".format(portal_ap)
    print "AP from link creation: {0}".format(link_ap)
    print "AP from field creation: {0}".format(field_ap)
    print "Total AP: {0}".format(portal_ap+link_ap+field_ap)

if __name__ == "__main__":
    main()

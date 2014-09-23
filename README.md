# Introduction

This is for Ingress. If you don't know what that is, you're lost.

This code is designed to make a plan for linking a given set of portals in the
way (and the order) that creates the most fields. This is harder than it sounds.
If you're working on more than a dozen portals, learning to use this code may
be faster than planning by hand.

This code follows the procedure in this [YouTube video][0].


# Prerequisites

You'll need [Python][2] (I've got 2.7) as well as networkx, numpy, matplotlib and Pillow.

You can get these setup easily with the [Enthought Python Distribution][1]. (Probably, I haven't tried it)

On windows, it is STRONGLY recommended to use the above python distribution or at least to find precompiled versions of the required libraries. DO NOT ATTEMPT TO USE PIP. That way lies madness. 

You can use [pip][3] to install the dependencies via:

    pip install -r requirements.txt

Before you do that, make sure you have these libraries available:

    sudo apt-get install python-dev libfreetype6-dev libpng-dev libjpeg62 libjpeg62-dev

# Example

I'll be distributing this code with a file test.csv. Try running

    python makePlan.py -n 4 -s 75 test.csv

This will put a bunch of files into the "test/" directory (see OUTPUT FILE LIST)

Now try running

    python makePlan.py -n 3 -s 75 test/test-<timestamp>.pkl

This uses the plan stored in the .pkl file instead of calculating a new one. It will create files for 3 agents instead of 4.

### OUTPUT FILE LIST

	keyPrep.txt
		List of portals, their numbers on the map, and how many keys are needed

	keys_for_agent_M_of_N.txt
		List of keys agent number M will need (if N agents are participating)

	links_for_agent_M_of_N.txt
		List of ALL the links
		Total distance traveled and AP earned by agent number M
			- Except for the links marked with a star (*), the links should be made IN THE ORDER LISTED
			- Links with a star can be made out of order, but only EARLY i.e. BEFORE their position in the list (this can save you time)
			- The links that agent number M makes are marked with underscores__
			- The first portal listed is the origin portal (where the agent must be)
			- The second portal listed is the destination portal (for which the agent must have a key)

	portalMap.png
		A map showing the locations of the portals
	linkMap.png
		A map showing the locations of portals and links
			- Up is north
			- Portal numbers increase from north to south
			- Portal numbers match "keyPrep.txt" and "linkes_for_agent_M_of_N.txt"
			- Link numbers match those in the link schedules "links_for_agent_M_of_N.txt"

	ownershipPrep.txt
		List of portals whose first link is incoming
			- These portals need to be captured and fully powered before the linking operation
		List of portals whose first link is outgoing
			- You may be able to save time by capturing and fully powering these portals DURING the linking operation

	`*`.pkl
		A Python pickle file containing all portal and plan information
			- The default name is "*<name of the csv file>*-*<timestamp>*.pkl"

# Warranty

No promises

# Usage

    python makePlan.py [-g] [-n <agent_count>] [-s <extra_samples>] <input_file>

    -g:            Include this option if you like your maps green instead of blue for inexplicable reasons

    agent_count:   Number of agents for which to make a plan

    extra_samples: Number of iterations to run optimization

    input_file:  One of two types of files:
        .csv   format:
            PORTAL NAME, INTEL MAP LINK, (OPTIONAL:) NUMBER OF KEYS AVAILABLE

            Example:
            Cupid's Span, https://www.ingress.com/intel?ll=37.791541,-122.390014&z=17&pll=37.791541,-122.390014, 3

            if portal name contains commas, wrap it in quotes. Example: "Zipcar, 12345"
            keys (optional parameter) is the number of keys you have for the portal
            If you leave this blank, the program assumes you have no keys

        .pkl   an output from a previous run of this program
            this can be used to make the same plan with a different number of agents

# Notes

The space of possible max-field plans is large. Rather than trying every
possibility, this program randomly tries some plans and presents you with one
that doesn't require you to obtain too many more keys.

If you don't like the plan you got, run it again. You'll probably get a
different plan.


[0]: https://www.youtube.com/watch?v=priezq6Dm4Y
[1]: https://www.enthought.com/downloads/
[2]: https://www.python.org/download/releases/2.7
[3]: https://pypi.python.org/pypi/pip

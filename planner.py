import os
import re
import subprocess
from shutil import copy as copyf
from copy import deepcopy
from model_parser.parser_new import parse_model
from model_parser.constants import *
from problemFileMaker import problemFileMaker
class Planner():
    CALL_FAST_DOWNWARD = 'planner/FAST-DOWNWARD/fast-downward.py '
    CALL_VAL = 'planner/VAL/validate -v '
    CALL_PR2 = 'planner/PR2/pr2plan'

    def __init__(self, domain='planner/domain.pddl', problem='planner/mock_problem.pddl', obs='planner/obs.dat'):
        # Domain and problem files
        self.domain = domain
        self.human_domain = 'planner/domain_human.pddl'
        self.problem = problem

        # Grounded pr-domain and pr-problem files
        self.pr_domain = 'pr-domain.pddl'
        self.pr_problem = 'pr-problem.pddl'
        self.val_pr_domain = 'planner/pr-domain.pddl'
        self.val_pr_problem = 'planner/pr-problem.pddl'

        # Plan output
        self.sas_plan = 'sas_plan'

        # Observation files
        self.obs = obs
        self.saveduiPlan = 'planner/saved_obs.dat'

        # Explanation files
        self.exc_file = 'planner/mmp/src/exp.dat'
        self.exp_file = 'planner/mmp_explanations/src/exp.dat'

        # Generating Landmarks
        self.landmark_code = 'planner/FD/src/fast-downward.py'
        self.output = 'output'

        self.resource_list = ['adminfire', 'mesafire', 'phxfire', 'scottsfire',
                    'joseph', 'lukes', 'apachestation', 'courtstation', 'substation']

        self.probMaker = problemFileMaker()
        self.observations = ''

    def deletePrFiles(self):
        try:
            os.remove(self.pr_domain)
            os.remove(self.pr_problem)
        except:
            print ("[WARNING] Problem deleting pr-domain and pr-problem files.  Probably they already don't exist!")

    def getLandmarks(self):
        try:
            cmd = '{0} {1} --landmarks name=lm_zg'.format(self.landmark_code, self.output)
            os.system(cmd)
        except:
            raise Exception('[ERROR] In generating landmarks')

        f = open('landmark.txt', 'r')
        lm = []
        for l in f:
            if 'explained' not in l.lower():
                lm.append( l.split('Atom ')[1] )
        return lm
    def getActionNames(self):
        self.deletePrFiles()
        try:
            cmd = self.CALL_PR2 + ' -d ' + self.domain + ' -i ' + self.problem +' -o ' + 'planner/blank_obs.dat'
            os.system(cmd)
        except:
            raise Exception('[ERROR] Call to PR2 failed!')

        if not os.path.isfile( self.pr_domain ) or not os.path.isfile( self.pr_problem ):
            print ("[ERROR] Goal cannot be reached from initial state")
            return []

        try:
            cmd = 'cat {0} | grep -v "EXPLAIN" > pr-problem.pddl.tmp && mv pr-problem.pddl.tmp {0}'.format(self.pr_problem)
            os.system(cmd)
            cmd = 'cat {0} | grep -v "EXPLAIN" > pr-domain.pddl.tmp && mv pr-domain.pddl.tmp {0}'.format(self.pr_domain)
            os.system(cmd)
        except:
            raise Exception('[ERROR] Removing "EXPLAIN" from pr-domain and pr-problem files.')

        actionNames = []
        pr_model = parse_model(self.pr_domain,self.pr_problem)
        return list(pr_model[DOMAIN].keys())

        # f = open(self.pr_domain)
        # for l in f:
        #     if '(:action ' in l:
        #         actionNames.append('(' + l.split('(:action ')[1].strip() +')')
        # return actionNames

    def plan(self):
        try:
            cmd = self.CALL_FAST_DOWNWARD + self.pr_domain + ' ' + self.pr_problem + ' --search "astar(lmcut())"';
            os.system(cmd)
            print ('FAST-DOWNWARD called...')
        except:
            raise Exception('[ERROR] Running FAST-DOWNWARD!')

    def getImpResources(self):
        try:
            f = open(self.sas_plan, 'r')
        except:
            # If no plan exists for the present state
            self.plan()
            f = open(self.sas_plan, 'r')

        # Write plan to observation file
        resources = []
        for l in f:
            for r in self.resource_list:
                if (r in l.lower()) and (not r in resources):
                    resources.append(r)
        return resources

    def getExplanations(self):

        cmd = "cd planner/mmp_explanations/src && ./Problem.py -m ../../../{0} -n ../../../{1} -d ../domain/radar_domain_template.pddl -f ../../mock_problem.pddl".format(self.domain, self.human_domain)
        try:
            os.system(cmd)
        except:
            print ("[ERROR] while generating explanations for the present plan")

        try:
            f = open( self.exp_file, 'r' )
        except:
            print ("[WARNING] No explanations were generated.  Probably there is no model difference")
            return {1:"None"}
        reason = {}
        i = 1
        for l in f:
            s = l.strip()
            if not s:
                continue
            s = l.split('Explanation >> ')[1].strip()
            reason[i] = s
            i += 1
        return reason

    def getExcuses(self):
        cmd = "cd planner/mmp/src && ./Problem.py -m ../domain/radar_domain.pddl -n ../domain/radar_domain.pddl -d ../domain/radar_domain_template.pddl -q ../domain/complete_initial_state_problem_template.pddl -f ../domain/complete_initial_state_problem.pddl -t ../../mock_problem.pddl"
        try:
            os.system(cmd)
        except:
            print ("[ERROR] Error while generation explanations for changing initial state to make it feisable")

        f = open( self.exc_file, "r" )
        reason = ''
        for l in f:
            s = l.strip()
            if not s:
                continue
            s = l.split('Explanation >> has-initial-state-')[1].replace("has_", "Get ").replace("_number@", " ")
            reason = reason + s + ' '
        plan_actions = { '1' : 'INVALID_INITIAL_STATE ;{0}'.format(reason.replace('\n',' ')) }
        return plan_actions
    def savePlan(self):
        copyf(self.obs, self.saveduiPlan)

    def loadPlan(self):
        print( "[LOG] Copying {0} to {1}".format(self.saveduiPlan, self.obs) )
        copyf(self.saveduiPlan, self.obs)

    def getOrderedObservations(self):
        observations = {}
        f = open(self.obs)
        count = 1
        for l in f:
            observations[ count ] = l.strip()
            count += 1

        return observations
    def definePlanningProblem(self, gs):
        '''
        Creates the problem.pddl file
        @Input - Goal for which planning problem is to be made
        @Output - Creates problem.pddl
        '''

        tempProblem = "(define (problem BYENG) (:domain RADAR)\n\n(:objects \n"
        tempProblem += self.probMaker.addObjects()

        tempProblem += "\n)\n\n(:init\n"
        tempProblem += self.probMaker.addInitialState(gs)

        tempProblem += self.probMaker.addFireStationResources()
        tempProblem += self.probMaker.addHospitalResources()
        tempProblem += self.probMaker.addPoliceStationResources()

        tempProblem += self.probMaker.addDurationsOfActions()

        tempProblem += '\n)\n\n(:goal\n(and\n'
        tempProblem += self.probMaker.addGoal()

        tempProblem += ')\n)\n'
        tempProblem += '\n(:metric minimize (total-cost))\n\n)\n'

        f = open(self.problem, 'w')
        f.write(tempProblem)

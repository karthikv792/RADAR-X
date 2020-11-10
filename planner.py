import os
import re
import subprocess
from shutil import copy as copyf
from copy import deepcopy
from problemFileMaker import problemFileMaker
from model_parser.parser_new import parse_model
from model_parser.writer_new import ModelWriter
from model_parser.constants import *
from itertools import combinations
import multiprocessing as mp

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
        self.foil_obs = 'planner/foil_obs.dat'
        self.saveduiPlan = 'planner/saved_obs.dat'
        self.pref_obs = 'planner/Preferences/pref_obs.dat'

        # Explanation files
        self.exc_file = 'planner/mmp/src/exp.dat'
        self.exp_file = 'planner/mmp_explanations/src/exp.dat'
        self.foil_exp_file = 'planner/mmp_foil_explanations/src/exp.dat'

        # Generating Landmarks
        self.landmark_code = 'planner/FD/src/fast-downward.py'
        self.output = 'output'

        self.resource_list = ['adminfire', 'mesafire', 'phxfire', 'scottsfire',
                    'joseph', 'lukes', 'apachestation', 'courtstation', 'substation']

        self.probMaker = problemFileMaker()
        self.initial = True
        self.observations = ''
        self.ungrounded_actions = []
        self.consts = []
        self.prob_objects = []
        self.user_suggested_actions = []
        self.length = 0
        self.subset_comp = {}
        self.conflict_sets = []
        self.max_set = ()
        self.pref = []
        self.max_sets = []
        self.for_multiple_runs = False
        self.not_pref = []
        self.foil_actions_done = {}
        self.m=1
        self.plausible_sets = []
        self.cost_of_current_plan = 0


    def plan(self):
        try:
            cmd = self.CALL_FAST_DOWNWARD + self.pr_domain + ' ' + self.pr_problem + ' --search "astar(lmcut())"';
            os.system(cmd)
            print ('FAST-DOWNWARD called...')
        except:
            raise Exception('[ERROR] Running FAST-DOWNWARD!')

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

    def writeObservations(self, actions, tillEndOfPresentPlan=False):

        if tillEndOfPresentPlan:
            acts = deepcopy( actions )
            for i in range(len(acts.keys())-1, 0, -1):
                if ';--' not in acts[i]:
                    break
            actions = {}
            for j in range(0,i+1):
                actions[j] = acts[j]

        # Write plan to file in sas_plan style
        s = ''
        for k in sorted(actions):
            s += actions[k].strip() + '\n'

        f = open(self.obs, 'w')
        f.write(s)
        f.close()

    def writeFoilObservations(self, actions, file, tillEndOfPresentPlan=False):
        if tillEndOfPresentPlan:
            acts = deepcopy( actions )
            for i in range(len(acts.keys())-1, 0, -1):
                if ';--' not in acts[i]:
                    break
            actions = {}
            for j in range(0,i+1):
                actions[j] = acts[j]

        # Write plan to file in sas_plan style
        s = ''
        for k in sorted(actions):
            # print(actions[k].strip())
            spl = (re.sub('[(){}<>]', '', actions[k].strip())).replace(' ','').split('_')
            # print(spl)
            string = spl[0]
            for i in spl[1:]:
                if (i.lower() not in self.prob_objects):
                    string += '_' + i
                else:
                    string += ' ' + i
            # print(string)
            s += string + '\n'

        f = open(file, 'w')
        f.write(s)
        f.close()




    def reconcileModels(self, changes):
        print( changes )
        changeHumanModel = []
        changeRobotModel = []
        for key in list(changes.keys()):
            if '-reject' in key:
                act = key.split('-reject')[0]
                changeRobotModel.append( act )
                changes.pop( key, None )
                changes.pop( act, None )

        for key in list(changes.keys()):
            changeHumanModel.append( key )

        self.updateDomainFile(self.domain.split('.pddl')[0]+'_human.pddl', changeHumanModel)
        self.updateDomainFile(self.domain, changeRobotModel, True)

    def updateDomainFile(self, fname, changes, remove=False):
        if not changes:
            return

        act_updates = {}
        for c in changes:
            act, pre = c.split('-has-precondition-')
            act_updates[ act ] = pre

        print( "Updating ...\nfile: {0}\nremove: {1}\nchanges: {2}".format(fname, remove, act_updates) )
        print("Updating done")
        f = open(fname, 'r')
        s = ""
        removePredicate = False
        for l in f:
            if removePredicate:
                if prec in l:
                    removePredicate = False
                    continue
            if '(:action ' in l:
                act_name = l.split(':action ')[1].strip()
                try:
                    prec = act_updates[ act_name ]
                    if remove:
                        s += l
                        removePredicate = True
                    else:
                        s += l
                        s += prec + "\n"
                except:
                    s += l
                    continue
            else:
                s += l
        f.close()
        f = open(fname.split('.pddl')[0]+'_modify.pddl', 'w')
        f.write( s )
        f.close()
        print( "Updated '{0}'!".format(fname.split('.pddl')[0]+'_modify.pddl') )
        if remove:
            self.domain = fname.split('.pddl')[0]+'_modify.pddl'
        else:
            self.human_domain = fname.split('.pddl')[0]+'_modify.pddl'
        # model = parse_model(fname,self.problem)
        # for act in list(model[DOMAIN].keys()):
        #     try:
        #         prec = act_updates[act]
        #         if remove:
        #             for precs in model[DOMAIN][act][POS_PREC]:
        #                 if prec in precs:
        #                     model[DOMAIN][act][POS_PREC].remove(precs)
        #     except:
        #         continue
        # writer = ModelWriter(model)
        # writer.write_files(fname.split('.pddl')[0]+'_modify.pddl','problem.pddl')
        if remove:
            self.domain = fname.split('.pddl')[0]+'_modify.pddl'
        else:
            self.human_domain = fname.split('.pddl')[0]+'_modify.pddl'

    def getInitialPlan(self,tillEndOfPresentPlan=False):
        self.plan()
        plan_actions = {}
        f = open(self.sas_plan, 'r')
        i = 0
        for l in f:
            if '(general cost)' not in l:
                    plan_actions[i] = l.upper().strip()
                    i += 1
            else:
                cost=re.findall(r'\b\d+\b', l)
                self.cost_of_current_plan = int(cost[0])

        f.close()
        self.initial = False
        self.writeObservations(plan_actions, tillEndOfPresentPlan)
        copyf(self.pr_domain, self.val_pr_domain)
        copyf(self.pr_problem, self.val_pr_problem)

    def getSuggestedPlan(self, actions, tillEndOfPresentPlan=False):
        self.writeObservations(actions)

        # If actions are blank, use the present pr_domain and pr_problem files to
        # plan. If not, generate new files with the known actions to be explained.
        if actions:
            # Save the present domain
            copyf(self.pr_domain, self.val_pr_domain)
            copyf(self.pr_problem, self.val_pr_problem)
            try:
                print('\n=====\n{0}\n======\n'.format(self.obs))
                cmd = self.CALL_PR2 + ' -d ' + self.val_pr_domain + ' -i ' + self.val_pr_problem +' -o ' + self.obs
                os.system(cmd)
                print("PR2 DONE")
            except:
                raise Exception('[ERROR] In Call to PR2!')

        self.plan()


        # Write plan to observation file
        plan_actions = {}
        f = open(self.sas_plan, 'r')
        i = 0
        acts = [x.strip('() \n') for x in actions.values()]
        for l in f:
            if '(general cost)' not in l:
                if 'EXPLAIN_OBS_' in l.upper():
                    a = l.upper().replace('EXPLAIN_OBS_','').strip()
                    plan_actions[i] = re.sub('_[0-9]', '', a)
                    i += 1
                    '''
                    for a in acts:
                        if a.upper() in l.upper():
                            plan_actions[i] = '(' + a.upper().strip() + ' )'
                            i += 1
                            break
                    '''
                else:
                    plan_actions[i] = l.upper().strip() + ';--'
                    i += 1
            else:
                cost=re.findall(r'\b\d+\b', l)
                self.cost_of_current_plan = int(cost[0])
        f.close()
        self.writeObservations(plan_actions, tillEndOfPresentPlan)

    def getValidatedPlan(self, actions):
        self.writeObservations(actions)
        try:
            cmd = self.CALL_VAL + self.val_pr_domain + ' ' + self.val_pr_problem + ' ' + self.obs
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
        except:
            print('[ERROR] Failed to execute VAL on given plan')
        if out:
            out=out.decode()
            if 'Plan failed to execute' in out:
                print(out.split("Plan Repair Advice:\n"))
                faults = out.split("Plan Repair Advice:\n")[1].strip()
                if ')' in faults:
                    action_name = faults.split(') ')[0].strip().upper() +")"
                    reason = faults.split('\n\n')[0].strip().replace('\n', " : ")
                f = open(self.obs, 'w')
                for k in sorted(actions):
                    print (actions[k].strip('\n( )').lower(), action_name.strip('\n( )').lower())
                    if actions[k].strip('\n( )').lower() in action_name.strip('\n( )').lower():
                        f.write(actions[k].strip() + ';' + reason + '\n')
                    else:
                        f.write(actions[k].strip() + '\n')
                f.close()

    def validateFoil(self,actions):
        self.writeFoilObservations(actions,self.foil_obs)
        if actions:
            # Save the present domain
            copyf(self.pr_domain, self.val_pr_domain)
            copyf(self.pr_problem, self.val_pr_problem)
            try:
                print('\n=====\n{0}\n======\n'.format(self.observations))
                cmd = self.CALL_PR2 + ' -d ' + self.val_pr_domain + ' -i ' + self.val_pr_problem +' -o ' + self.obs
                os.system(cmd)
                print("PR2 DONE")
            except:
                raise Exception('[ERROR] In Call to PR2!')


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
            print ("[ERROR] Error while generation explanations for changing initial state to make it feasible")

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

    def deletePrFiles(self):
        try:
            os.remove(self.pr_domain)
            os.remove(self.pr_problem)
        except:
            print ("[WARNING] Problem deleting pr-domain and pr-problem files.  Probably they already don't exist!")

    def getActionNames(self):
        self.deletePrFiles()
        try:
            cmd = self.CALL_PR2 + ' -d ' + self.domain + ' -i ' + self.problem +' -o ' + 'planner/blank_obs.dat' + '> /dev/null 2>&1'
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
        pr_model = parse_model(self.pr_domain, self.pr_problem)
        return list(pr_model[DOMAIN].keys())
        # actionNames = []
        # f = open(self.pr_domain)
        # for l in f:
        #     if '(:action ' in l:
        #         actionNames.append('(' + l.split('(:action ')[1].strip() +')')
        # return actionNames

    def savePlan(self):
        copyf(self.obs, self.saveduiPlan)

    def loadPlan(self):
        print( "[LOG] Copying {0} to {1}".format(self.saveduiPlan, self.obs) )
        copyf(self.saveduiPlan, self.obs)

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

    def getOrderedObservations(self):
        observations = {}
        f = open(self.obs)
        count = 1
        for l in f:
            observations[ count ] = l.strip()
            count += 1

        return observations

    def getFoilObservations(self):
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
        f.close()
        self.parsed_model = parse_model('planner/domain1.pddl', self.problem)
        words = []
        for action in list(self.parsed_model[DOMAIN].keys()):
            for sub_word in action.split('_'):
                words.append(sub_word)
        self.ungrounded_actions = list(set(words))
        constants = []
        for i in self.parsed_model[CONSTANTS]:
            for word in i:
                constants.append(word)
        self.consts = list(set(constants))
        for i in self.parsed_model[CONSTANTS]:
            self.prob_objects.append(i[0])

    def getPreferredPlan(self,actions,tillEndOfPresentPlan=False):
        # present_actions = self.getOrderedObservations()
        # p_actions = [(re.sub('[(){}<>]', '', i)).replace(' ', '') for i in list(present_actions.values())]
        if type(actions)!=type(list()):
            foil_actions = [(re.sub('[(){}<>]', '', actions[i].split('\n')[1])).replace(' ', '') for i in sorted(actions.keys())]
        else:
            foil_actions = actions
        f, cost = self.solve_or_not(foil_actions,flag=2)
        plan_actions = {}
        if self.foil_actions_done:
            self.foil_actions_done = {}
        i = 0
        j = 0
        # acts = [x.strip('() \n') for x in actions.values()]
        for l in f:
            if 'general cost' not in l:
                # action = (re.sub('[(){}<>]', '', l.upper().strip())).replace(' ', '')
                print(l.upper().strip())
                if 'EXPLAIN_OBS' in l.upper():
                    actionn = l.upper().strip().replace('EXPLAIN_OBS_', '').replace('_1','')
                    self.foil_actions_done[j] = actionn + ';++'
                    plan_actions[i] = actionn + ';++'
                    i += 1
                    j += 1
                elif 'WITHOUT_OBS' in l.upper():
                    actionn = l.upper().strip().replace('_WITHOUT_OBS', '')
                    print(actionn)
                    self.foil_actions_done[j] = actionn + ';--'
                    # plan_actions[i] = l.upper().strip() + ';:' #.replace('_WITHOUT_OBS','')
                    # print(plan_actions[i])
                    j += 1
                else:
                    plan_actions[i] = l.upper().strip()
                    i += 1
            else:
                cost = re.findall(r'\b\d+\b', l)
                self.cost_of_current_plan = int(cost[0])

        self.writeObservations(plan_actions, tillEndOfPresentPlan)

    def getClosestPlan(self,actions,tillEndOfPresentPlan=False):
        # present_actions = self.getOrderedObservations()
        # p_actions = [(re.sub('[(){}<>]', '', i)).replace(' ', '') for i in list(present_actions.values())]
        if type(actions)!=type(list()):
            foil_actions = [(re.sub('[(){}<>]', '', actions[i].split('\n')[1])).replace(' ', '') for i in sorted(actions.keys())]
        else:
            foil_actions = actions
        self.user_suggested_actions = foil_actions
        # diff_actions = list(set(p_actions)-set(foil_actions))
        # print(diff_actions)
        try:
            self.soft_compile(foil_actions)
        except Exception as detail:
            print("[ERROR] While compiling actions into a planning problem ", detail)
        try:
            cmd = self.CALL_FAST_DOWNWARD + 'write_pr_domain.pddl' + ' ' + 'write_pr_problem.pddl' + ' --search "astar(lmcut())"'
            os.system(cmd)
            print ('FAST-DOWNWARD called...')
        except:
            raise Exception('[ERROR] Running FAST-DOWNWARD!')


        f = open(self.sas_plan, 'r')
        plan_actions = {}
        if self.foil_actions_done:
            self.foil_actions_done = {}
        i = 0
        j=0
        # acts = [x.strip('() \n') for x in actions.values()]
        for l in f:
            if 'general cost' not in l:
                # action = (re.sub('[(){}<>]', '', l.upper().strip())).replace(' ', '')
                print(l.upper().strip())
                if 'WITH_OBS' in l.upper():
                    actionn = l.upper().strip().replace('_WITH_OBS','')
                    self.foil_actions_done[j] = actionn + ';++'
                    plan_actions[i] = actionn  + ';++'
                    i+=1
                    j+=1
                elif 'WITHOUT_OBS' in l.upper():
                    actionn = l.upper().strip().replace('_WITHOUT_OBS', '')
                    print(actionn)
                    self.foil_actions_done[j] = actionn + ';--'
                    # plan_actions[i] = l.upper().strip() + ';:' #.replace('_WITHOUT_OBS','')
                    # print(plan_actions[i])
                    j += 1
                else:
                    plan_actions[i] = l.upper().strip()
                    i+=1
            else:
                cost=re.findall(r'\b\d+\b', l)
                self.cost_of_current_plan = int(cost[0])
        f.close()
        self.writeObservations(plan_actions, tillEndOfPresentPlan)


    def writePreferenceObservations(self, actions, tillEndOfPresentPlan=False):
        if tillEndOfPresentPlan:
            acts = deepcopy( actions )
            for i in range(len(acts.keys())-1, 0, -1):
                if ';--' not in acts[i]:
                    break
            actions = {}
            for j in range(0,i+1):
                actions[j] = acts[j]
        print([i for i in actions])
        # Write plan to file in sas_plan style
        s = ''
        for spl in actions:
            string = spl.split('_')
            act = string[0]
            for i in string[1:]:
                if (i.lower() not in self.prob_objects):
                    act += '_' + i
                else:
                    act += ' ' + i
            s += act + '\n'

        f = open(self.pref_obs, 'w')
        f.write(s)
        f.close()

    def solve_or_not(self,current,flag=0):
        # lock.acquire()
        self.writePreferenceObservations(current)

        CALL_Pref_PR2 = 'planner/Preferences/PR2/pr2plan'
        try:
            cmd = CALL_Pref_PR2 + ' -d ' + self.domain + ' -i '+self.problem+' -o ' + self.pref_obs + '> /dev/null 2>&1'
            # cmd = CALL_PR2 + ' -d ../../domain.pddl -i ../../mock_problem.pddl -o ' + self.partial_foil + '> /dev/null 2>&1'
            os.system(cmd)
        except:
            raise Exception('[ERROR] Call to PR2 failed')
        if not current:
            try:
                cmd = 'cat {0} | grep -v "EXPLAIN" > pr-problem.pddl.tmp && mv pr-problem.pddl.tmp {0}'.format(
                    self.pr_problem)
                os.system(cmd)
                cmd = 'cat {0} | grep -v "EXPLAIN" > pr-domain.pddl.tmp && mv pr-domain.pddl.tmp {0}'.format(
                    self.pr_domain)
                os.system(cmd)
            except:
                raise Exception('[ERROR] Removing "EXPLAIN" from pr-domain and pr-problem files.')
        # lock.release()
        return self.get_plan(self.pr_domain, self.pr_problem,flag)

    def get_plan(self,domainFileName, problemFileName,flag=0):
        if flag==0:
            # print "command",__FD_PLAN_CMD__.format(domainFileName, problemFileName)
            __FD_PLAN_CMD__ = "planner/Preferences/./get_plan.sh {} {} {}"
            # print("command", __FD_PLAN_CMD__.format(domainFileName, problemFileName))
            plan_outputs = []
            output = os.popen(__FD_PLAN_CMD__.format(domainFileName, problemFileName,self.m)).read().strip()
            print(output)
            # plan   = [item.strip().replace('_', ' ') for item in output.split('\n')] if output != '' else []
            if output!= '':
                if 'Solution found.' in output:
                    return True
                plan = [item.strip() for item in output.split('\n')]
            else:
                plan = []
            print(plan)
            if len(plan)!=0:
                return True
            else:
                return False
        else:
            __FD_PLAN_CMD__ = "planner/Preferences/./fd_plan.sh {} {}"
            __FD_PLAN_COST_CMD__ = "planner/Preferences/./plan_cost.sh"
            output = os.popen(__FD_PLAN_CMD__.format(domainFileName, problemFileName)).read().strip()

            # plan   = [item.strip().replace('_', ' ') for item in output.split('\n')] if output != '' else []
            plan = [item.strip() for item in output.split('\n')] if output != '' else []
            if flag==1:
                if len(plan) > 0:
                    return True
                else:
                    return False
            elif flag==2:
                if len(plan) > 0:
                    output1 = os.popen(__FD_PLAN_COST_CMD__).read().strip()
                    cost = int(output1)
                else:
                    cost = -1
                return plan, cost




        # print "plan","\n".join(plan)

    def __getstate__(self):
        """ This is called before pickling. """
        state = self.__dict__.copy()
        del state['probMaker']
        return state

    def __setstate__(self, state):
        """ This is called while unpickling. """
        self.__dict__.update(state)

    def par_init(self,l):
        global lock
        lock = l
    def parallel_loo(self,subset,pref):
        if subset in self.subset_comp.keys():
            return None
        if any(sett in self.not_pref for sett in subset):
            return None
        if subset in self.conflict_sets:
            print("ITEM IN CONF", subset)
            return None
        if pref=='plausible':
            if True in [all(s in i['key'] for s in subset) for i in self.plausible_sets]:
                return None
        return [subset, self.solve_or_not(subset)]
    def getPreference(self, actions, not_pref=None,tillEndOfPresentPlan=False):
        foil_actions = [(re.sub('[(){}<>]', '', actions[i].split('\n')[1])).replace(' ', '') for i in sorted(actions.keys())]
        if self.for_multiple_runs==True:
            self.length = 0
            self.subset_comp = {}
            self.conflict_sets = []
            self.max_set = ()
            self.pref = []
            self.not_pref = []
            self.max_sets=[]
            self.for_multiple_runs = False
            self.m=1
        actions = foil_actions
        if not_pref!=None:
            if not_pref not in self.not_pref:
                self.not_pref += not_pref
                self.not_pref = list(set(self.not_pref))
            for i in self.conflict_sets:
                for j in i:
                    if j!=not_pref[0] and j not in self.not_pref and j not in self.pref:
                        self.pref.append(j)
        while self.m<5:
            while self.length <= len(actions):
                # pool = mp.Pool(mp.cpu_count())
                l = mp.Lock()
                pool = mp.Pool(initializer=self.par_init, initargs=(l,))
                subsets = combinations(actions, self.length)
                results = [pool.apply(self.parallel_loo, args = (subset,not_pref)) for subset in subsets]
                pool.close()
                for item in results:
                    if item is None:
                        continue
                    subset, solved = item[0], item[1]
                    print("----------------------SUBSET",subset,solved)
                    if not solved:
                        self.subset_comp[subset] = [False,len(subset)]
                        self.conflict_sets.append(subset)
                        self.conflict_sets = list(set(self.conflict_sets))
                        print("not plan subset",subset)
                        children = combinations(subset,1)
                        dict1 =  [{'key':list(subset),'value':False}]
                        for k in children:
                            if (k in self.subset_comp.keys()) and self.subset_comp[k][0]==True:
                                dict1+= [{'key': list(k), 'value': self.subset_comp[k][0]}]
                        print(self.conflict_sets)
                        print(dict1)
                        return dict1, False
                    else:
                        self.subset_comp[subset] = [True, len(subset)]
                        # if len(self.pref)==0:
                        #     if len(self.max_set)<len(subset):
                        #         self.max_set = subset
                        #         self.max_sets = []
                        #     else:
                        #         self.max_sets.append(self.max_set)
                        #         self.max_sets.append(subset)
                        # else:
                        #     if all(item in subset for item in self.pref):
                        #         if len(self.max_set) < len(subset):
                        #             self.max_set = subset
                        #             self.max_sets = []
                        #         else:
                        #             self.max_sets.append(self.max_set)
                        #             self.max_sets.append(subset)
                        #     elif any(item in subset for item in self.pref):
                        #         self.max_sets.append(self.max_set)
                        #         self.max_sets.append(subset)

                self.length += 1
                print(self.length)
            self.length=0
            self.m+=1
            if any(False in s for s in list(self.subset_comp.values())):
                break
        self.for_multiple_runs = True
        #run closestplan
        for act in self.not_pref:
            actions.remove(act)
        final_actions = actions
        print("FINAL", final_actions)
        return final_actions, True

    def soft_compile(self,actions):
        pr_model = parse_model(self.val_pr_domain,self.val_pr_problem)
        obs = {}
        obs[PARARMETERS] = []
        obs[POS_PREC] = []
        obs[ADDS] = []
        obs[DELS] = []
        obs[FUNCTIONAL] = [[['total-cost', 'number'], [9, 'Integer']]]
        obs[COND_ADDS] = []
        obs[COND_DELS] = []
        for i in range(len(actions)):
            action = actions[i]
            if action in list(pr_model[DOMAIN].keys()):
                temp_obs = deepcopy(pr_model[DOMAIN][action])
                temp_without_obs = deepcopy(obs)
                # temp_without_obs[FUNCTIONAL][0][1][0] = temp_obs[FUNCTIONAL][0][1][0]
                action_with_obs = action + '_WITH_OBS'
                action_without_obs = action + '_WITHOUT_OBS'
                predicate = [(action + '_MET_OBS').lower(), []]
                pr_model[PREDICATES].append(predicate)
                pr_model[INSTANCE][GOAL].append(predicate)
                temp_obs[ADDS].append(predicate)
                temp_without_obs[ADDS].append(predicate)
                if i != 0:
                    prev_action = actions[i - 1]
                    for i in pr_model[DOMAIN][prev_action + '_WITHOUT_OBS'][ADDS]:
                        temp_obs[POS_PREC].append(i)
                        temp_without_obs[POS_PREC].append(i)
                pr_model[DOMAIN][action_with_obs] = temp_obs
                pr_model[DOMAIN][action_without_obs] = temp_without_obs
        pr_write = ModelWriter(pr_model)
        pr_write.write_files('write_pr_domain.pddl','write_pr_problem.pddl')

    def getFoilExplanations(self,actions):
        foil_actions = [(re.sub('[(){}<>]', '', actions[i].split('\n')[1])).replace(' ', '') for i in sorted(actions.keys())]
        self.writeFoilObservations(actions,self.foil_obs)
        if self.for_multiple_runs==True:
            self.for_multiple_runs = False
            self.m=1
        subsets = combinations(foil_actions, len(foil_actions))
        results = [[subset,self.solve_or_not(subset,flag=0)] for subset in subsets]
        print(results)
        for result in results:
            if result[1]:
                f, cost = self.solve_or_not(result[0],flag=2)
                print("COST",cost)
                if cost!=-1:
                    if cost!=self.cost_of_current_plan:
                        return {0:"valid",1:cost,2:self.cost_of_current_plan}
                    else:
                        self.getInitialPlan()
                        return {0:"same_cost",1:cost,2:self.cost_of_current_plan}
                else:
                    return self.getExplanations()
        cmd = "cd planner/mmp_foil_explanations/src && ./Problem.py -m ../../../{0} -n ../../../{1} -d ../domain/radar_domain_template.pddl -f ../../mock_problem.pddl -pf ../../foil_obs.dat ".format(self.domain, self.human_domain)
        try:
            os.system(cmd)
        except:
            print("[ERROR] while generating explanations for the present plan")

        try:
            f = open(self.foil_exp_file, 'r')
        except:
            print("[WARNING] No explanations were generated.  Probably there is no model difference")
            return {1: "None"}
        reason = {}
        i = 1
        for l in f:
            s = l.strip()
            if not s:
                continue
            s = l.split('Explanation >> ')[1].strip()
            reason[i] = s
            i += 1
        print(reason)
        return reason

    def getPlausibleSets(self, actions):
        foil_actions = [(re.sub('[(){}<>]', '', actions[i].split('\n')[1])).replace(' ', '') for i in
                        sorted(actions.keys())]
        if self.for_multiple_runs==True:
            self.plausible_sets = []
            self.for_multiple_runs = False
            self.m=1
        m_solution = False
        length = len(foil_actions)
        while self.m < 5:

            while length >= 0:
                # pool = mp.Pool(mp.cpu_count())
                l = mp.Lock()
                pool = mp.Pool(initializer=self.par_init, initargs=(l,))
                subsets = combinations(foil_actions, length)
                results = [pool.apply(self.parallel_loo, args=(subset, 'plausible')) for subset in subsets]
                pool.close()

                for item in results:
                    if item is None:
                        continue
                    subset, solved = item[0], item[1]
                    print("----------------------SUBSET", subset, solved)
                    if solved:
                        re_solved = self.solve_or_not(subset, 1)
                        if re_solved:
                            self.plausible_sets += [{'key': list(subset)}]
                    else:
                        m_solution = True
                length -= 1
            length = 0
            self.m += 1
            if m_solution == True:
                break
            self.plausible_sets = []
        self.for_multiple_runs = True
        return self.plausible_sets



(define (domain RADAR)

(:requirements :typing :strips :equality :action-costs )

;; TYPES
(:types		police fire transport medic - agents
			hospital policestation firestation pois - location
)

;; PREDICATES

(:predicates	(alerted ?loc - location)
	     		(updated ?a - agents)
	     		(deployed_police_cars ?at - location)
	     		(deployed_engines ?at - location)
	     		(deployed_small_engines ?at - location)
	     		(deployed_big_engines ?at - location)
	     		(deployed_ladders ?at - location)
	     		(deployed_bulldozers ?at - location)
	     		(deployed_helicopters ?at - location)
	     		(deployed_rescuers ?at - location)
	     		(deployed_ambulances ?at - location)
	     		(positioned_policemen ?at - location)
	     		(media_contacted ?a - agents)
	     		(active_helpline ?a - agents)
	     		(active_local_alert ?a - agents)
	     		(blocked_road ?from - location ?to - location)
	     		(traffic_diverted ?from - location ?to - location)
	     		(prepared_evacuation ?from - location)
	     		(evacuated ?from - location ?to - location)
	     		(extinguished_fire ?at - location)
	     		(fire_at ?at - location)
	     		(small_fire_at ?at - location)
	     		(barricaded ?at - location)
	     		(searched ?at - location)
	     		(attended_casualties ?at - location)
	     		(addressed_media)
	     		(needed_barricade ?at - location)
	     		(needed_active_local_alert ?a - agents)
	     		(needed_diverted_traffic ?from - location ?to - location)
	     		(needed_search_casualties ?at - location)
	     		(needed_attend_casualties ?at - location)
	     		(needed_address_media)
			    (not_needed_barricade ?at - location)
	     		(not_needed_active_local_alert ?a - agents)
	     		(not_needed_diverted_traffic ?from - location ?to - location)
	     		(not_needed_search_casualties ?at - location)
	     		(not_needed_attend_casualties ?at - location)
	     		(not_needed_address_media)
			(has_police_car_number ?from - location)
			(has_small_engines_number ?from - location)
			(has_big_engines_number ?from - location)
			(has_ladders_number ?from - location)
			(has_helicopters_number ?from - location)
			(has_rescuers_number ?from - location)
			(has_ambulances_number ?from - location)
			(has_policemen_number ?from - location)
			(has_bulldozers_number ?from - location)
			(sent_social_media ?from - location)
			(no_social_media)


)


;; FUNCTIONS 

(:functions 
	(duration_unit_actions)
	(duration_deploy_police_cars)
	(duration_deploy_small_engines)
	(duration_deploy_big_engines)
	(duration_deploy_ladders)
	(duration_deploy_bulldozers)
	(duration_deploy_helicopters)
	(duration_deploy_rescuers)
	(duration_deploy_ambulances)
	(duration_position_policemen)
	(duration_contact_media)
	(duration_set_up_helpline)
	(duration_issue_local_alert)
	(duration_block_road)
	(duration_prepare_evacuation)
	(duration_evacuation)
	(duration_extinguish_small_fire)
	(duration_extinguish_big_fire)
	(duration_barricade)
	(duration_search_casualties)
	(duration_sent_signal)
	(duration_attend_casualties)
	(duration_address_media)
	(total-cost)
)

;; ACTIONS / OPERATORS

(:action deploy_small_engines
:parameters (?a - fire ?from - firestation ?to - pois)
:precondition
(and
( has_small_engines_number ?from )
)
:effect
(and
( deployed_small_engines ?to )
( deployed_engines ?to )
( increase (total-cost) (duration_deploy_small_engines) )
(not ( has_small_engines_number ?from ))
(not ( alerted ?from ))
)
)

(:action address_media
:parameters (?a - agents)
:precondition
(and
( no_social_media )
( media_contacted ?a )
( needed_address_media )
)
:effect
(and
( not_needed_address_media )
( addressed_media )
( increase (total-cost) (duration_address_media) )
(not ( needed_address_media ))
)
)

(:action extinguish_big_fire
:parameters (?a - fire ?at - pois)
:precondition
(and
( fire_at ?at )
( deployed_big_engines ?at )
)
:effect
(and
( needed_search_casualties ?at )
( extinguished_fire ?at )
( increase (total-cost) (duration_extinguish_big_fire) )
(not ( fire_at ?at ))
(not ( not_needed_search_casualties ?at ))
)
)

(:action block_road
:parameters (?a - transport ?from - location ?to - location)
:precondition
(and
( active_local_alert ?a )
( positioned_policemen ?from )
( deployed_police_cars ?from )
( positioned_policemen ?to )
( deployed_police_cars ?to )
)
:effect
(and
( increase (total-cost) (duration_block_road) )
( needed_active_local_alert ?a )
( needed_diverted_traffic ?from ?to )
( blocked_road ?from ?to )
(not ( not_needed_diverted_traffic ?from ?to ))
(not ( not_needed_active_local_alert ?a ))
)
)

(:action barricade
:parameters (?a - fire ?at - pois)
:precondition
(and
( deployed_engines ?at )
)
:effect
(and
( not_needed_barricade ?at )
( barricaded ?at )
( increase (total-cost) (duration_barricade) )
( needed_active_local_alert ?a )
(not ( needed_barricade ?at ))
(not ( not_needed_active_local_alert ?a ))
)
)

(:action send_social_media
:parameters (?from - pois ?at - pois)
:precondition
(and
( searched ?at )
)
:effect
(and
( sent_social_media ?from )
( increase (total-cost) (duration_sent_signal) )
(not ( no_social_media ))
)
)

(:action issue_local_alert
:parameters (?a - agents)
:precondition
(and
( media_contacted ?a )
)
:effect
(and
( active_local_alert ?a )
( not_needed_active_local_alert ?a )
( increase (total-cost) (duration_issue_local_alert) )
(not ( needed_active_local_alert ?a ))
)
)

(:action deploy_helicopters
:parameters (?a - fire ?from - firestation ?to - pois)
:precondition
(and
( has_helicopters_number ?from )
( alerted ?from )
)
:effect
(and
( deployed_helicopters ?to )
( increase (total-cost) (duration_deploy_helicopters) )
(not ( alerted ?from ))
(not ( has_helicopters_number ?from ))
)
)

(:action deploy_rescuers
:parameters (?a - fire ?from - firestation ?to - pois)
:precondition
(and
( has_rescuers_number ?from )
)
:effect
(and
( deployed_rescuers ?to )
( increase (total-cost) (duration_deploy_rescuers) )
(not ( has_rescuers_number ?from ))
(not ( alerted ?from ))
)
)

(:action update
:parameters (?a - agents)
:precondition
(and

)
:effect
(and
( updated ?a )
( increase (total-cost) (duration_unit_actions) )

)
)

(:action deploy_police_cars
:parameters (?a - police ?from - policestation ?to - pois)
:precondition
(and
( has_police_car_number ?from )
( alerted ?from )
)
:effect
(and
( deployed_police_cars ?to )
( increase (total-cost) (duration_deploy_police_cars) )
(not ( has_police_car_number ?from ))
(not ( alerted ?from ))
)
)

(:action alert
:parameters (?a - agents ?loc - location)
:precondition
(and

)
:effect
(and
( increase (total-cost) (duration_unit_actions) )
( alerted ?loc )

)
)

(:action contact_media
:parameters (?a - agents)
:precondition
(and

)
:effect
(and
( media_contacted ?a )
( increase (total-cost) (duration_contact_media) )

)
)

(:action extinguish_small_fire
:parameters (?a - fire ?at - pois)
:precondition
(and
( fire_at ?at )
( small_fire_at ?at )
( deployed_engines ?at )
)
:effect
(and
( needed_address_media )
( extinguished_fire ?at )
( needed_search_casualties ?at )
( increase (total-cost) (duration_extinguish_small_fire) )
(not ( not_needed_search_casualties ?at ))
(not ( small_fire_at ?at ))
(not ( not_needed_address_media ))
(not ( fire_at ?at ))
)
)

(:action evacuate
:parameters (?a - police ?from - location ?to - location)
:precondition
(and
( prepared_evacuation ?from )
( blocked_road ?from ?to )
( deployed_police_cars ?from )
( positioned_policemen ?from )
)
:effect
(and
( increase (total-cost) (duration_evacuation) )
( evacuated ?from ?to )

)
)

(:action divert_traffic
:parameters (?a - transport ?from - location ?to - location)
:precondition
(and
( blocked_road ?from ?to )
( active_local_alert ?a )
)
:effect
(and
( traffic_diverted ?from ?to )
( not_needed_diverted_traffic ?from ?to )
( increase (total-cost) (duration_unit_actions) )
(not ( needed_diverted_traffic ?from ?to ))
)
)

(:action deploy_bulldozers
:parameters (?a - fire ?from - firestation ?to - pois)
:precondition
(and
( alerted ?from )
( has_bulldozers_number ?from )
)
:effect
(and
( increase (total-cost) (duration_deploy_bulldozers) )
( deployed_bulldozers ?to )
(not ( alerted ?from ))
(not ( has_bulldozers_number ?from ))
)
)

(:action search_casualties
:parameters (?a - fire ?at - pois)
:precondition
(and
( deployed_rescuers ?at )
( deployed_bulldozers ?at )
( deployed_helicopters ?at )
( extinguished_fire ?at )
)
:effect
(and
( needed_address_media )
( searched ?at )
( needed_attend_casualties ?at )
( increase (total-cost) (duration_search_casualties) )
(not ( not_needed_address_media ))
(not ( not_needed_attend_casualties ?at ))
)
)

(:action set_up_helpline
:parameters (?a - agents)
:precondition
(and
( media_contacted ?a )
)
:effect
(and
( active_helpline ?a )
( increase (total-cost) (duration_set_up_helpline) )

)
)

(:action deploy_ambulances
:parameters (?a - police ?from - hospital ?to - pois)
:precondition
(and
( has_ambulances_number ?from )
( alerted ?from )
)
:effect
(and
( increase (total-cost) (duration_deploy_ambulances) )
( deployed_ambulances ?to )
(not ( has_ambulances_number ?from ))
(not ( alerted ?from ))
)
)

(:action attend_casualties
:parameters (?a - medic ?at - pois)
:precondition
(and
( deployed_ambulances ?at )
( needed_attend_casualties ?at )
)
:effect
(and
( attended_casualties ?at )
( needed_address_media )
( increase (total-cost) (duration_attend_casualties) )
( not_needed_attend_casualties ?at )
(not ( no_social_media ))
(not ( not_needed_address_media ))
(not ( needed_attend_casualties ?at ))
)
)

(:action position_policemen
:parameters (?a - police ?from - policestation ?to - pois)
:precondition
(and
( alerted ?from )
( has_policemen_number ?from )
)
:effect
(and
( positioned_policemen ?to )
( increase (total-cost) (duration_position_policemen) )
(not ( alerted ?from ))
)
)

(:action deploy_big_engines
:parameters (?a - fire ?from - firestation ?to - pois)
:precondition
(and
( has_big_engines_number ?from )
)
:effect
(and
( deployed_engines ?to )
( increase (total-cost) (duration_deploy_big_engines) )
( deployed_big_engines ?to )
(not ( alerted ?from ))
(not ( has_big_engines_number ?from ))
)
)

(:action prepare_evacuation
:parameters (?a - police ?from - location)
:precondition
(and
( active_local_alert ?a )
)
:effect
(and
( increase (total-cost) (duration_prepare_evacuation) )
( prepared_evacuation ?from )

)
)

(:action deploy_ladders
:parameters (?a - fire ?from - firestation ?to - pois)
:precondition
(and
( deployed_big_engines ?to )
( alerted ?from )
( has_ladders_number ?from )
)
:effect
(and
( increase (total-cost) (duration_deploy_ladders) )
( deployed_ladders ?to )
(not ( alerted ?from ))
(not ( has_ladders_number ?from ))
)
)


)

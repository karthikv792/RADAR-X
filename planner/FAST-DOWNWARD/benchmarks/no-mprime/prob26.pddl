(define
  (problem strips-mprime-x-26)
  (:domain no-mystery-prime-strips)
  (:objects auggen koendringen schallstadt haltingen waldkirch
      guendlingen freiburg emmendingen wittlingen kleinkems gottenheim
      hugstetten kuebelwagen krankenwagen fahrrad muellabfuhr segway
      apfel broiler halber-hirsch kukuruz fuel-0 fuel-1 fuel-2 fuel-3
      fuel-4 fuel-5 capacity-0 capacity-1 capacity-2 capacity-3)
  (:init
    (at apfel waldkirch)
    (at broiler guendlingen)
    (at fahrrad guendlingen)
    (at halber-hirsch wittlingen)
    (at krankenwagen waldkirch)
    (at kuebelwagen koendringen)
    (at kukuruz kleinkems)
    (at muellabfuhr emmendingen)
    (at segway kleinkems)
    (capacity fahrrad capacity-1)
    (capacity krankenwagen capacity-1)
    (capacity kuebelwagen capacity-1)
    (capacity muellabfuhr capacity-2)
    (capacity segway capacity-3)
    (capacity-number capacity-0)
    (capacity-number capacity-1)
    (capacity-number capacity-2)
    (capacity-number capacity-3)
    (capacity-predecessor capacity-0 capacity-1)
    (capacity-predecessor capacity-1 capacity-2)
    (capacity-predecessor capacity-2 capacity-3)
    (connected auggen kleinkems)
    (connected auggen schallstadt)
    (connected emmendingen gottenheim)
    (connected emmendingen hugstetten)
    (connected freiburg koendringen)
    (connected freiburg waldkirch)
    (connected freiburg wittlingen)
    (connected gottenheim emmendingen)
    (connected gottenheim guendlingen)
    (connected gottenheim kleinkems)
    (connected gottenheim waldkirch)
    (connected guendlingen gottenheim)
    (connected guendlingen haltingen)
    (connected guendlingen hugstetten)
    (connected guendlingen waldkirch)
    (connected haltingen guendlingen)
    (connected haltingen hugstetten)
    (connected haltingen wittlingen)
    (connected hugstetten emmendingen)
    (connected hugstetten guendlingen)
    (connected hugstetten haltingen)
    (connected hugstetten wittlingen)
    (connected kleinkems auggen)
    (connected kleinkems gottenheim)
    (connected koendringen freiburg)
    (connected koendringen schallstadt)
    (connected schallstadt auggen)
    (connected schallstadt koendringen)
    (connected waldkirch freiburg)
    (connected waldkirch gottenheim)
    (connected waldkirch guendlingen)
    (connected wittlingen freiburg)
    (connected wittlingen haltingen)
    (connected wittlingen hugstetten)
    (fuel auggen fuel-0)
    (fuel emmendingen fuel-4)
    (fuel freiburg fuel-4)
    (fuel gottenheim fuel-5)
    (fuel guendlingen fuel-5)
    (fuel haltingen fuel-1)
    (fuel hugstetten fuel-4)
    (fuel kleinkems fuel-1)
    (fuel koendringen fuel-1)
    (fuel schallstadt fuel-2)
    (fuel waldkirch fuel-0)
    (fuel wittlingen fuel-1)
    (fuel-number fuel-0)
    (fuel-number fuel-1)
    (fuel-number fuel-2)
    (fuel-number fuel-3)
    (fuel-number fuel-4)
    (fuel-number fuel-5)
    (fuel-predecessor fuel-0 fuel-1)
    (fuel-predecessor fuel-1 fuel-2)
    (fuel-predecessor fuel-2 fuel-3)
    (fuel-predecessor fuel-3 fuel-4)
    (fuel-predecessor fuel-4 fuel-5)
    (location auggen)
    (location emmendingen)
    (location freiburg)
    (location gottenheim)
    (location guendlingen)
    (location haltingen)
    (location hugstetten)
    (location kleinkems)
    (location koendringen)
    (location schallstadt)
    (location waldkirch)
    (location wittlingen)
    (package apfel)
    (package broiler)
    (package halber-hirsch)
    (package kukuruz)
    (vehicle fahrrad)
    (vehicle krankenwagen)
    (vehicle kuebelwagen)
    (vehicle muellabfuhr)
    (vehicle segway))
  (:goal
    (and
      (at broiler koendringen))))

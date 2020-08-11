breed [believers believer]
breed [disbelievers disbeliever]
breed [recovers recover]
globals [infected_per infected_mean infected_list

  ]
turtles-own [
  Beliefs ; B = 1 if believes; B = -1 if doesn't believe; 
  Strength  ; strength of belief varies from 0 to 1 
  Compliance ; binary; 1 if complies/enforces norm, and 0 otherwise.  
  Enforcement ; 1 if enforces norm; -1 if enforces deviance.   
  Enforcement_Need ; Wi = 1-(Bi/Ni)SumCj / 2  
       ;; is just the proportion of i's neighbors whose behavior does not conform with it's Beliefs B
  Enforcement_Need_2  ;; same # but divided by 2; as used in the article.
  N_Neighbors
  Convert
  
]

;; CODE:
;; BELIEVERS = arrow, DISBELIEVERS = default shape
;; COMPLIANCE = RED, DEVIANCE = BLUE
;; ENFORCEMENT = HEADING TO THE RIGHT (90) ; NO ENFORCEMENT = HEADING TO THE LEFT (270)


;; Basic MODEL of ED:  1.  agents observe neighbors compliance and enforcement.  2.  Each agent then makes two decisions:  
;; (i) whether to comply with the norm, and (ii) whether to enforce the norm.   

to setup
   __clear-all-and-reset-ticks
  
  let IB initial_believers
  let ID population - IB

    ;if Condition = "Local Random" OR Condition = "Global"  [    
     create-believers IB [ 
     set size 1 set color red    
      setxy random-pxcor random-pycor
      while [any? other turtles-here] [ let empty_patch one-of patches with [any? turtles-here = false] move-to empty_patch ]     
    ]
     
 if Condition = "Local Clustered" [ 
      let a 20
      let b 12
      let p patch 20 12
      
      let d (list believers)
      foreach d [
       ask ? [move-to p
       set p patch-at-heading-and-distance 45 1]
      ]
      
      ]
    
 ask believers[
         set Beliefs 1
         set Strength 1 ;; by default all true believers initially comply!
         set compliance 1
         set convert 0
         
         set shape "arrow" 
         set heading 90  ; NO INITIAL ENFORCEMENT
 ]
   
   create-disbelievers ID [ 
         set size 1 set color blue  ; BLUE COLOR BECAUSE NOT COMPLYING WITH 
         setxy random-pxcor random-pycor
         while [any? other turtles-here] [ let empty_patch one-of patches with [any? turtles-here = false] move-to empty_patch ]
         set Beliefs -1
         set Strength random-float 0.38
         set convert 0
         
         set compliance -1
         set heading 90 ; NO INITIAL ENFORCEMENT
   ]

   ask turtles [setup-map]
   
end



to START!

ED
  update-plots
end


to setup-map

           if Condition = "Global" [set N_Neighbors Other Turtles]
    if Condition = "Local Clustered" OR Condition = "Local Random" [  
      set N_Neighbors turtle-set turtles-on neighbors
      
      
      if small_worlds? = true [
       
        small-worlds
      ]
      
      
         ]

 
end



to ED
  ask turtles [

      if small_worlds? = true AND Continuous-Rewiring? = true AND Condition != "Global" [

        small-worlds
      ]


   let Ni_list (list N_Neighbors)
   let Ni count N_Neighbors
   if Ni = 0 [set Ni 1]
   let Bi [Beliefs] of self
   let NCi count N_Neighbors with [Compliance = Bi]

    set Enforcement_Need 1 - (NCi / Ni)
    set Enforcement_Need_2 Enforcement_Need / 2
   ; output-print Enforcement_Need_2

COMPLY?
ENFORCE?
    
  ]
  
end


TO COMPLY?
  ;; disbeliever complies if the proportion of neighbors enforcing compliance is greater than the strength of disbeliever's belief;
   let S [strength] of self
   let Bi [Beliefs] of self
   let Ej count N_Neighbors with [Enforcement = -1 * Bi] ;; neighbors enforcing opposite belief
   let Ni count N_Neighbors
   if Ni = 0 [set Ni 1]
   
   ifelse (Ej / Ni) > S [set compliance -1 * Bi] [set compliance Bi]
   
  if Compliance = 1 [set color red]
  if Compliance = -1 [set color blue]
   
   
end

to ENFORCE?
  
   let S [strength] of self
   let Bi [Beliefs] of self
   let Ci [Compliance] of self
   let Ej count N_Neighbors with [Enforcement = -1 * Bi] ;; neighbors enforcing opposite belief
   let Ni count N_Neighbors
   if Ni = 0 [set Ni 1]
   let Wi Enforcement_Need_2
  
     ifelse (Ej / Ni) > (S + K) AND Bi != Ci [set Enforcement -1 * Bi] 
     ; Enforcement is opposite of belief if:
     ; a) the proportion of enforcement against belief is greater than the strength of belief plus the cost of enforcement, AND
     ; b) agent already complies against agent's own belief; violates one's own belief already.
     ;; THIS MEANS THAT AGENTS CANNOT ENFORCE COMPLIANCE UNLESS THEY HAVE ALREADY COMPLIED.  
     [
     
     ifelse S * Wi > K AND Bi = Ci [set Enforcement Bi] 
     [set Enforcement 0]
     
     
     ]
     
     
     if enforcement = 1 [set heading 270] ;; to better visualize enforcement
     
 if conversion? = true [CV] 
end

to CV
  let a conversion / 10000   ; 1 will equal .0001 - the learning parameter set in the article
  
  if Enforcement != Beliefs [
   set convert convert - (a * Enforcement * Beliefs) 
   
   if convert > Strength AND Beliefs != compliance [
     hatch-believers 1 [ set color red set Beliefs 1 set compliance 1 set convert 0  
         set shape "arrow" 
         set heading 90  
     ];;  NOTICE THAT I AM NOT RESETTING THE STRENGTH OF THEIR CONVICTIONS.  THESE NEW CONVERTS ARE A LESS CONVINCED GROUP OF BELIEVERS THAN THE ORIGINAL!
     die ;; THE ORIGINAL DISBELIVER DIES
     ]
    
  ]
  
end

to small-worlds

let a self
let N_list [] 
let h turtle-set turtles-on neighbors
let g turtle-set N_Neighbors
; ask N_Neighbors [set color yellow] 
ask N_Neighbors [

      ;; whether to rewire it or not?
      ifelse (random-float 1) < rewiring-probability
      [
      
      
      let b  (turtle-set a h g) ; a = self, original turtle; N_neighbors list here includes this turtle replacing itself with another random turtle
      let c one-of turtles
      while [member? c b = true] [set c one-of turtles]  ; keeps changing the turtle until it isn't itself or a neighbor
       
          ask a [set N_list fput c N_list]
          ;  set N_list replace-item (? - 1) N_list c
          ;show N_list
          ask c [set color brown]
            ]
      [ask a [set N_list fput myself N_list]] ;;myself or self?
]
        ;; must be ? - 1 to replace the correct turtle
   
   ask a [set N_Neighbors turtle-set N_list] ; must go back and ask original turtle to do this!

end


to-report prcnt_comply
  let comply count turtles with [compliance = 1]
  let Ni count turtles
  if Ni = 0 [set Ni Ni + 1]
  report (comply / Ni) * 100
   
end

to-report prcnt_enforce
  let enforce count turtles with [enforcement = 1]
  let Ni count turtles
  if Ni = 0 [set Ni Ni + 1]
  report (enforce / Ni) * 100
   
end

to-report prcnt_believe
  let B count believers
  let Ni count turtles
  if Ni = 0 [set Ni Ni + 1]
  report (B / Ni) * 100
   
end

to-report false_comply ;; proportion of disbelievers who falsely comply
  let D count disbelievers
  if D = 0 [set D D + 1]
  let F count disbelievers with [Compliance = 1]
  report (F / D) * 100
end

to-report false_enforce
let D count disbelievers
if D = 0 [set D D + 1]
let F count disbelievers with [Enforcement = 1]
report (F / D) * 100

end
@#$#@#$#@
GRAPHICS-WINDOW
142
10
592
316
-1
-1
11.0
1
10
1
1
1
0
1
1
1
0
39
0
24
0
0
1
ticks
30.0

BUTTON
2
10
65
43
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
65
10
120
43
NIL
START!
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
1
44
141
77
population
population
10
1000
1000
10
1
NIL
HORIZONTAL

SLIDER
-3
78
141
111
Initial_Believers
Initial_Believers
0
population
10
5
1
NIL
HORIZONTAL

PLOT
598
10
1140
233
Percentage of Agents that Comply and Enforce
NIL
NIL
0.0
10.0
0.0
100.0
true
true
"" ""
PENS
"% Comply" 1.0 0 -2674135 true "" "plot prcnt_comply"
"% Enforce" 1.0 0 -16777216 true "" "plot prcnt_enforce"
"% Believe" 1.0 0 -7500403 true "" "plot prcnt_believe"
"% False Compliance" 1.0 0 -955883 true "" "plot false_comply"
"% False Enforce" 1.0 0 -6459832 true "" "plot false_enforce"

TEXTBOX
217
325
663
403
Believers = Arrow, Disbelievers = Default\nCompliance with Believers = RED, Deviance from Believers =  BLUE\nEnforcement = Heading to Left (270) <-- ; No Enforcement = Heading to Right (90) -->\nBy default, all true believers initially comply; S = 1.  \nBrown agents are those connected via \"Small Worlds\" linking.
11
0.0
1

MONITOR
789
233
933
278
Average Links per Node
(count links) / population
2
1
11

SLIDER
-2
112
146
145
Influence_Range
Influence_Range
1
20
10
1
1
NIL
HORIZONTAL

SLIDER
-2
145
146
178
K
K
0
.5
0.125
.005
1
NIL
HORIZONTAL

MONITOR
597
234
788
279
Mean Conviction of Disbelievers
mean [strength] of disbelievers
2
1
11

CHOOSER
0
180
138
225
Condition
Condition
"Global" "Local Clustered" "Local Random"
2

MONITOR
596
280
758
325
% of False Compliance
false_comply
2
1
11

MONITOR
759
280
909
325
% of False Enforcement
false_enforce
2
1
11

SLIDER
1
275
139
308
Conversion
Conversion
0
10
10
1
1
NIL
HORIZONTAL

SWITCH
1
243
138
276
Conversion?
Conversion?
1
1
-1000

SWITCH
5
329
159
362
small_worlds?
small_worlds?
0
1
-1000

SLIDER
5
363
198
396
rewiring-probability
rewiring-probability
0
.5
0.01
.01
1
NIL
HORIZONTAL

SWITCH
5
396
180
429
Continuous-Rewiring?
Continuous-Rewiring?
0
1
-1000

@#$#@#$#@
## WHAT IS IT?

This model is derived from and inspired by:  
Centola, Damon, Robb Willer, and Michael Macy. “The Emperor’s Dilemma: A Computational Model of Self‐Enforcing Norms.” American Journal of Sociology 110, no. 4 (January 1, 2005): 1009–1040.

The basic idea is to test under what conditions people will not only comply with norms they privately disbelieve (i.e. 'FALSE COMPLIANCE'), but also when they will actively enforce them (i.e. 'FALSE ENFORCEMENT').  

EMPEROR'S DILEMMA ROUTINE:
1.  agents observe neighbors compliance and enforcement.  
2.  Each agent then makes two decisions:  
(i) whether to comply with the norm, and 
(ii) whether to enforce the norm.  



## HOW IT WORKS
Below are the main agent variables:
Beliefs:  B = 1 if believes; B = -1 if doesn't believe.
Strength (of Belief): varies from 0 to 1 
Compliance:  1 if agent complies with the norm, and 0 the agent does not comply.  Enforcement:  1 if agent enforces norm, -1 if enforces deviance, and 0 if agent doesn't enforce at all.

First, agents must decide whether to comply with the norm.  In this model, a disbeliever complies if the proportion of neighbors enforcing compliance is greater than the strength of disbeliever's belief.  For example, if the strength of disbelief is .5, but 60% of an agent's neighbors are enforcing compliance, then this agent will also comply.  Thus, this depends on the question of enforcement, given next.

Second, agents make a decision to enforce based on whether those around them are complying with their private norms.  In this model, the "Need to Enforce" is inversely related to the proportion of neighbors complying with their private beliefs! This is a somewhat strange assumption.  In practice, it means that an isolated individual constituting an extreme minority is more likely to impose his or her beliefs on others when nobody else believes them.   A more plausible approach is that groups are more likely to enforce norms on minorities, but that will wait for another model.  Because of this assumption, enforcement drops whenever full compliance is achieved, causing the system to swing back towards non-compliance.

Note that the parameter "K" refers to the Cost of Enforcement.  

"Rewiring probability" here is the same as that used in "Small Worlds" algorithm, but instead of rewiring links, it asks each neighbor and randomly assigns one of these neighbors to an agentset N_Neighbors if probability is below "rewiring probability".  The "Small Worlds" parameter will set up small-worlds links.  At the limit, where re-wiring probability = 1, small-worlds is the same as the global condition.   

## Other Assumptions

- No hypocritical enforcement;  Agents can only enforce compliance if they also complied, and can only enforce deviance if they have deviated.

- Initial condition is that agents conform to their own private beliefs and no one enforces anything.

- In the article, strength of belief, S, of disblievers ranges 0 < S <= .38  The mean of their conviction is 0.19.  


## THINGS TO TRY

Change the "Conversion" setting.  Conversions allow the beliefs of agents to change according to a stochastic process.  

The parameter K (cost of enforcement) was fixed in the article cited above.  It turns out that the interesting results do not obtain when the cost is varied.

There are several conditions in which this model can be run:  

- Global:  Each agent can interact with any other agent.

- Local: Each agent can interact only with its N closest neighbors, where N is set by "Influence_Range."  There are two local conditions:  i)  Clustered, or ii) Random.   These refer to whether the BELIEVERS are initially clustered or randomly distributed.  

The interesting finding of this article is that cascades of false compliance and false enforcement will only be generated if the BELIEVERS (i.e. zealots) are initially clustered together, and agents can only interact locally (i.e. they lack global or outside information).


## CREDITS AND REFERENCES

Centola, Damon, Robb Willer, and Michael Macy. “The Emperor’s Dilemma: A Computational Model of Self‐Enforcing Norms.” American Journal of Sociology 110, no. 4 (January 1, 2005): 1009–1040.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270

@#$#@#$#@
NetLogo 5.0.5
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180

@#$#@#$#@
0
@#$#@#$#@

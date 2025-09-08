**“LLM translated” Version**

**0\. Core Data Types**

Pitch = str # e.g. "C4", "F#3"

Mode = Enum("Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Ionian")

Species = Enum("Authentic", "Plagal")

Motion = Enum("Parallel", "Similar", "Contrary", "Oblique")

Cantus = List\[Pitch\] # immutable input

Counterpt = List\[Pitch\] # mutable, one element per cantus note

State = {

"cantus" : Cantus,

"cp" : Counterpt,

"mode" : Mode,

"species" : Species,

"position" : "above" | "below" # user choice for CP placement

}

**1\. Mode-Detection Routine (§ 1)**

def detect_mode(cantus: Cantus) -> tuple\[Mode, Species\]:

final = cantus\[-1\] # 1.1

pitches = set(cantus) # 1.2-Method-step-1

candidates = \[\] # 1.2-Method-step-2

for mode in six_modes: # pre-coded table from § 1.2

if all( pitch in modal_scale(final, mode)

or pitch == licensed_accidental(final, mode)

for pitch in pitches ):

candidates.append(mode)

if len(candidates) == 0:

raise ModalError("Cantus is non-modal")

low, high = ambitus(cantus, final) # 1.3

species = "Plagal" if low <= -4 and high <= +5 else "Authentic"

mode = resolve_by_cadence(cantus, final, species, candidates) # 1.4

audit_accidentals(cantus, mode) # 1.5

return mode, species # 1.6

**2\. Note-Generation Loop (§ 6)**

def build_counterpoint(state: State) -> Counterpt:

for idx, cf_note in enumerate(state\["cantus"\]):

candidates = legal_consonant_pitches(cf_note, state) # § 2

\# Depth-first search with backtracking

placed = False

for cp_note in candidates:

if validate_all_rules(state, cf_note, cp_note, idx):

state\["cp"\].append(cp_note)

placed = True

break

if not placed: # 6.3 backtracking

back_up(state) # erase previous CP note(s)

return build_counterpoint(state)

return state\["cp"\]

**3\. Rule-Validation Pipeline (§ 6.2)**

def validate_all_rules(state, cf, cp, i) -> bool:

return ( vertical_consonance(cp, cf, state) # 6.2-1 & § 2

and motion_ok(cp, state, i) # 6.2-2 & § 3

and no_hidden_parallels(cp, state, i) # 6.2-3 & § 3.3

and melodic_ok(cp, state, i) # 6.2-4 & § 4

and spacing_ok(cp, state, i) # 6.2-5 & § 5

and accidental_ok(cp, state, i)) # 6.2-6 & § 1.5

**3.1 Vertical Consonance (§ 2)**

def vertical_consonance(cp, cf, state):

interval = get_interval(cp, cf, state\["position"\])

if interval not in perfect+imperfect: return False # 2.1-2

if cadence_penult(cf, state, interval) is False: return False

return consonance_balance_ok(state) # 2.1-3

**3.2 Motion Rules (§ 3)**

def motion_ok(cp, state, i):

if i == 0: return True

motion = classify_motion(state\["cp"\]\[i-1\], cp,

state\["cantus"\]\[i-1\], state\["cantus"\]\[i\])

prev_int = classify_interval(state\["cp"\]\[i-1\], state\["cantus"\]\[i-1\], state)

curr_int = classify_interval(cp, state\["cantus"\]\[i\], state)

return motion_matrix\[prev_int\]\[curr_int\](motion) # implements table § 3.2

**3.3 Forbidden Parallels & Hidden Perfects (§ 3.3)**

def no_hidden_parallels(cp, state, i):

if i == 0: return True

return not forms_parallel_5th_or_8ve(state\["cp"\]\[i-1\], cp,

state\["cantus"\]\[i-1\], state\["cantus"\]\[i\])

**3.4 Melodic Fitness (§ 4)**

def melodic_ok(cp, state, i):

line = state\["cp"\]

return ( leap_size_ok(line, i) # 4.1

and leap_compensation_ok(line, i) # 4.2

and no_pitch_triplet(line, i) # 4.3

and no_melodic_tritone(line, i) # 4.4

and within_range(line\[i\]) ) # 4.5

**3.5 Spacing / Voice-Crossing (§ 5)**

def spacing_ok(cp, state, i):

interval = abs(semitone_distance(cp, state\["cantus"\]\[i\]))

return ( interval <= 18 # ≤ 11th (5.3)

and not excessive_closeness(cp, state, i)

and acceptable_crossing(cp, state, i) ) # 5.2

**3.6 Modal & Accidental Compliance (§ 1.5)**

def accidental_ok(cp, state, i):

if is_accidental(cp):

cf_last_idx = len(state\["cantus"\]) - 1

if i == cf_last_idx - 1 and leading_tone_ok(cp, state): return True

if removes_mi_fa_tritone(state\["cp"\], i): return True

return False

return True

**4\. Helper Tables & Predicates**

- perfect = {"P1","P5","P8"}
- imperfect = {"m3","M3","m6","M6"}
- motion_matrix implements the four legal progressions (3.2).
- modal_scale(final, mode) returns the diatonic pitch-set of that mode.
- licensed_accidental(...) implements § 1.2 third column.

**5\. Interface End-Points**

| **Function** | **Input** | **Output** | **Behaviour** |
| --- | --- | --- | --- |
| analyse_mode(cantus) | Cantus | (Mode, Species) | Throws ModalError on failure. Implements section 1. |
| generate_counterpoint(cantus, position) | Cantus, "above"/"below" | Counterpt | Returns a fully-validated CP or raises NoSolutionError. Relies on rules 2–6. |
| validate_counterpoint(cantus, cp, position) | Cantus, Counterpt, "above"/"below" | True / list\[RuleError\] | Checks an existing CP against _all_ constraints, reporting first violation encountered. |

**Usage Example (in an LLM-powered composition endpoint)**

cantus = \["D4","E4","F4","G4","A4","G4","F4","E4","D4"\] # Dorian

mode, species = analyse_mode(cantus)

state = {

"cantus" : cantus,

"cp" : \[\],

"mode" : mode,

"species" : species,

"position" : "above" # user choice

}

counterpoint = generate_counterpoint(\*\*state)

If generate_counterpoint exhausts every branch without success it throws NoSolutionError, signalling that _with the current cantus_ no first-species line can satisfy every rule (rare but possible).

**This specification is deterministic and exhaustive:**

- Every rule in sections 1–5 translates to a boolean predicate.
- Section 6 becomes a depth-first search with backtracking driven by those predicates.
- The API surfaces _analyse_, _generate_, and _validate_ endpoints, allowing any LLM or external program to enforce or explore strict first-species counterpoint exactly as in Fux’s _Gradus_.
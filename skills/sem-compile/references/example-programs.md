# Example Sem programs

## Contents

- [1. Leaving a soul-crushing job — compact](#1-leaving-a-soul-crushing-job--compact)
- [2. Leaving a soul-crushing job — verbose](#2-leaving-a-soul-crushing-job--verbose)
- [3. Fan-out, hidden analysis, and synthesis](#3-fan-out-hidden-analysis-and-synthesis)
- [4. Mapping over claims and selecting across results](#4-mapping-over-claims-and-selecting-across-results)
- [5. Bounded iteration and semantic choice](#5-bounded-iteration-and-semantic-choice)
- [What variation is allowed](#what-variation-is-allowed)

These examples calibrate interpretation, not syntax. Each program is followed
by an execution inventory so it can be understood without the conversation
that produced it. Entries marked **local** are program-local functions; all
other named functions use an existing repository skill with the matching slug.

## 1. Leaving a soul-crushing job — compact

Source intent: clarify the tension, then return a story, song, and joke in that
order. Named artist references have already been lowered to broad mechanisms;
the applications are not asked to imitate a living or historical person's
distinctive voice.

```haskell
use [question-forge, parable, lyric, joke]

leavingMyJob =
  let dilemma =
        Question
          { choice = Stay <|> Leave
                     -- an unresolved pair of live options, not a route
                     -- choice or semantic application
          , gains  = [highPay, respect]
          , costs  = [drudgery, lossOfSoul]
          }

      core =
        let question = dilemma >>> questionForge
        in extractTension { dilemma = dilemma, question = question }
            -- local, one pass: return a CreativeBrief with the situation,
            -- forged question, one primary opposed pair, and at most two
            -- supporting pairs; preserve both sides and invent no facts

      outputs =
        core
        >>> ( parable `with`
                { mode = bureaucraticSurrealism
                , mechanisms =
                    [dreamLogic, trappedProtagonist,
                     escalatingInstitutionalLogic]
                }

              &&& lyric `with`
                { form = narrativeFolkBallad
                , mechanisms =
                    [recurringRefrain, propheticImagery, slantRhyme,
                     plainspokenDefiance, moralAmbiguity]
                }

              &&& joke `with`
                { form = shortDeadpanShaggyDog
                , engine = suspiciousLiteralism
                , mechanisms =
                    [apparentDigressionThatPlantsTheHinge,
                     delayedFrameShift, anticlimacticPunchline]
                , constraint = oneRecoverableTwoFrameTurn
                }
            )

  in hide [dilemma, core]
     >>> reveal outputs
     >>> order [Story, Song, Joke]
```

The record construction, visibility declarations, and ordering are structural.
The compact pipeline contains five applications:

| ID | Application | Input | Depends on | Result |
| --- | --- | --- | --- | --- |
| 1 | `question-forge` | `dilemma` | source | Forged question |
| 2 | **local** `extractTension` | dilemma and forged question | 1 | Creative brief |
| 3 | `parable` | creative brief | 2 | Story |
| 4 | `lyric` | creative brief | 2 | Song |
| 5 | `joke` | creative brief | 2 | Joke |

Applications 3–5 are independent fan-out branches. The visible returns are
Story, Song, and Joke in that order.

## 2. Leaving a soul-crushing job — verbose

This is a second valid compilation of the same request. Its extra ceremony
makes initial interpretation and local function contracts explicit.

```haskell
use [question-forge, parable, lyric, joke]

local understand(rawRequest: Text) -> Dilemma:
  extract only the stated situation, rewards, costs, and live choice
  preserve uncertainty and the speaker's own intensity
  return one standalone Dilemma; stop after one faithful pass
  do not advise, diagnose, or add biography

local extractTension(input: { dilemma: Dilemma, question: ForgedQuestion })
  -> CreativeBrief:
  select one primary opposed pair and at most two supporting pairs
  require support from the input and keep both sides as live goods
  return situation + forged question + tensions; stop after one brief
  do not decide whether the speaker should stay or leave

leavingMyJob :: Program [Artifact]
leavingMyJob = do
  dilemma <-
    understand
      "thinking about leaving my job; high pay and respect, but the work
       feels like drudgery and soul-loss"

  question <-
    questionForge
      ("Should I stay or leave?" `groundedIn` dilemma)

  tension <-
    extractTension { dilemma = dilemma, question = question }

  story <-
    parable tension `with`
      { mode = bureaucraticSurrealism
      , mechanisms = [dreamLogic, alienation, helplessEscalation]
      }

  song <-
    lyric tension `with`
      { form = narrativeFolkBallad
      , mechanisms = [recurringRefrain, propheticImagery,
                      slantRhyme, moralAmbiguity]
      }

  joke <-
    joke tension `with`
      { form = shortDeadpanShaggyDog
      , engine = literalization
      , mechanisms = [apparentDigressionThatPlantsTheHinge,
                      delayedFrameShift, anticlimacticPunchline]
      , constraint = oneRecoverableTwoFrameTurn
      }

  hide [dilemma, question, tension]
  pure [story, song, joke] >>> order [Story, Song, Joke]
```

The phrase `groundedIn` structurally packages two already-existing values; it
does not interpret them. This version contains six applications:

| ID | Application | Input | Depends on | Result |
| --- | --- | --- | --- | --- |
| 1 | **local** `understand` | raw request text | source | Dilemma |
| 2 | `question-forge` | surface question plus dilemma | 1 | Forged question |
| 3 | **local** `extractTension` | dilemma and forged question | 1, 2 | Creative brief |
| 4 | `parable` | creative brief | 3 | Story |
| 5 | `lyric` | creative brief | 3 | Song |
| 6 | `joke` | creative brief | 3 | Joke |

Applications 4–6 are independent once application 3 completes. Only Story,
Song, and Joke are returned, in that order.

## 3. Fan-out, hidden analysis, and synthesis

```haskell
use [assumption-audit, inversion, analogy-transfer]

local synthesizeLaunchAdvice(input: { audit, antiFailurePlan, transfers })
  -> Recommendation:
  identify agreements and real conflicts across all three artifacts
  prefer guards supported by the audit and transfers that survive disanalogy
  return one conditional recommendation plus its cheapest next test
  stop after one recommendation; do not erase minority evidence

launchReview(plan) = do
  audit <- assumptionAudit plan

  branches <-
    { plan = plan, audit = audit }
    >>> ( inversion `with` { goal = plan.launchGoal }
          &&& analogyTransfer `with`
                { problem = plan.adoptionProblem,
                  requireOneDistantDomain = true }
        )

  recommendation <-
    synthesizeLaunchAdvice
      { audit = audit
      , antiFailurePlan = branches.inversion
      , transfers = branches.analogyTransfer
      }

  hide branches
  pure [audit, recommendation]
  >>> order [Assumptions, Recommendation]
```

| ID | Application | Input | Depends on | Result |
| --- | --- | --- | --- | --- |
| 1 | `assumption-audit` | launch plan | source | Assumption audit |
| 2 | `inversion` | plan and audit | 1 | Anti-failure plan |
| 3 | `analogy-transfer` | plan and audit | 1 | Candidate transfers |
| 4 | **local** `synthesizeLaunchAdvice` | results 1–3 | 1, 2, 3 | Recommendation |

Applications 2 and 3 are independent branches. Their results remain traceable
but hidden from the final presentation. The visible returns are Assumptions and
Recommendation, in that order.

## 4. Mapping over claims and selecting across results

```haskell
use [assumption-audit]

local splitClaims(memo: Text) -> [SourcedClaim]:
  extract distinct consequential claims in source order
  attach the shortest supporting quotation or location to each
  return at most five claims; stop when another claim would be redundant
  do not turn questions, examples, or rhetorical flourishes into claims

local selectPortfolioKeystone(audits: [AssumptionAudit]) -> Keystone:
  compare each audit's keystone by load, confidence, and test cost
  return the single assumption whose failure threatens the most claims,
  naming ties or incomparable evidence instead of inventing precision
  stop after one cross-audit comparison

memoAudit(memo) = do
  claims <- splitClaims memo

  audits <-
    claims
    >>> map (assumptionAudit `with` { preserveSourceLink = true })
        -- one independent application per claim; collect results in the
        -- claims' source order; retain a failed item's place and status

  portfolioKeystone <- selectPortfolioKeystone audits.successful

  pure [audits, portfolioKeystone]
  >>> order [ClaimAuditsInSourceOrder, PortfolioKeystone]
```

If `splitClaims` returns `n` claims, this program contains `n + 2` applications:

| Pattern | Application | Input | Depends on | Result |
| --- | --- | --- | --- | --- |
| 1 | **local** `splitClaims` | memo | source | Up to five sourced claims |
| 2..n+1 | one `assumption-audit` per claim | exactly one sourced claim | 1 | One audit per claim |
| n+2 | **local** `selectPortfolioKeystone` | successful audits | all map applications | Portfolio keystone |

All mapped audit applications are mutually independent. The returned audit
collection preserves source order and failed positions; the cross-audit
keystone follows it.

## 5. Bounded iteration and semantic choice

```haskell
use [decision-matrix, first-principles-thinking]

local frameDecision(raw: Text) -> DecisionFrame:
  state the choice or governing question without inventing options
  retain explicit constraints and uncertainty
  return one frame; stop after one faithful pass

local sharpen(frame: DecisionFrame) -> DecisionFrame:
  make one consequentially vague term observable or answerable
  preserve settled details and do not add advice
  return one revised frame; stop after one material clarification

local stableEnough(input: { previous, current }) -> BooleanWithReason:
  true only when the options or governing question, stakes, and constraints
  are materially unchanged; compare meaning, not wording
  return one verdict and one-sentence reason; stop after one comparison
  do not treat a wording-only change as semantic progress

local chooseByShape(
  input: DecisionFrame,
  routes: decisionMatrix <|> firstPrinciplesThinking
) -> ChosenRoute:
  choose decision-matrix only when input names 2-6 concrete alternatives
  with enough evidence to elicit criteria; otherwise choose
  first-principles-thinking; never run both and never decide the issue here
  return one route identity; stop after one selection

clarifyThenAnalyze(raw) = do
  current <- frameDecision raw

  repeat at most 3 rounds, returning the latest frame on exhaustion:
    next <- sharpen current
    done <- stableEnough { previous = current, current = next }
    if done then current = next and stop
            else current = next and continue

  route <- chooseByShape
             { input = current
             , routes = decisionMatrix <|> firstPrinciplesThinking
             }

  result <- apply route to current
  pure result
```

`apply route` invokes the one selected repository skill; it is not a third
analysis function. If the loop runs `r` rounds (`1 <= r <= 3`), the program
contains `2r + 3` applications:

| Pattern | Application | Input | Depends on | Result |
| --- | --- | --- | --- | --- |
| 1 | **local** `frameDecision` | raw text | source | Initial decision frame |
| each round | **local** `sharpen` | current frame | prior frame/verdict | Revised frame |
| each round | **local** `stableEnough` | previous and revised frames | that round's `sharpen` | Stop verdict |
| after loop | **local** `chooseByShape` | final frame and two route contracts | final verdict | Chosen route |
| terminal | `decision-matrix` **or** `first-principles-thinking` | final frame | route choice | Analysis |

The loop is sequential; no round begins before the prior stopping verdict. The
choice is a semantic application, and exactly one terminal branch runs. Only
the terminal analysis is visible.

## What variation is allowed

All five programs could be rewritten with fewer symbols, different names,
tables, prose paragraphs, or new locally glossed constructs. A rewrite remains
equivalent when a fresh reader recovers the same meaningful applications,
declared inputs, dependencies, stopping behavior, visibility, and return order.
Valid Sem need not be valid Haskell.

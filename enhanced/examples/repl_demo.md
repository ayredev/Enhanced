# Enhanced REPL — Demo Session

This is a recorded REPL session showing Enhanced in action.

```
$ enhanced

Enhanced 0.1.0
Type English to code. Type 'help' for commands. Type 'exit' to quit.
──────────────────────────────────────────────────

> say "Hello, World"
Hello, World

> the number x is 5.

> the number y is 10.

> add x and y then say the result.
15

> the text name is "Alice".

> say name.
Alice

> create a list called team.

> add "Alice" to team.

> add "Bob" to team.

> add "Charlie" to team.

> vars
  x: number = 5
  y: number = 10
  result: number = 15
  name: text = Alice
  team: list = ['Alice', 'Bob', 'Charlie']

> create a new person called hero.

> check if hero is still valid.

> say the result.
True

> free hero.

> check if hero is still valid.

> say the result.
False

> open the file "notes.txt" as my_notes.

> write "Enhanced is amazing" to my_notes.

> close my_notes.

> say "File written safely."
File written safely.

> history
    1  say "Hello, World"
    2  the number x is 5.
    3  the number y is 10.
    4  add x and y then say the result.
    5  the text name is "Alice".
    6  say name.
    7  create a list called team.
    8  add "Alice" to team.
    9  add "Bob" to team.
   10  add "Charlie" to team.
   11  create a new person called hero.
   12  check if hero is still valid.
   13  say the result.
   14  free hero.
   15  check if hero is still valid.
   16  say the result.
   17  open the file "notes.txt" as my_notes.
   18  write "Enhanced is amazing" to my_notes.
   19  close my_notes.
   20  say "File written safely."

> save "my_session.en"
  Session saved to my_session.en

> clear
  Session cleared.

> vars
  (no variables defined)

> say ghost.
  ✗ 'ghost' hasn't been defined yet.
    Try: the number ghost is 0.

> the number a is 100.

> the number b is 200.

> add a and b then say the result.
300

> exit
Goodbye!
```

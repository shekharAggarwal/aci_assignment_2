# ACI Assignment 2 (AIMLZG557, S1-26) - Group 107

Situated Learning Assignment. Due **Sunday 22 November 2026, 11:59 PM**.

| Part | Status | File |
|---|---|---|
| Question 1: Connect Four with depth-3 Minimax (group, 5 marks) | Done | `Question1_Group.ipynb` |
| Question 2: workplace knowledge base (individual, 5 marks) | Shekhar's PDF done; other members write their own | `pdfs/<BITS ID>.pdf` |

## Folders

- `Question1_Group.ipynb`: the group solution. Use *Run All*, then play in the last cell.
- `pdfs/2025AG05925.pdf`: Shekhar's Question 2 (production release approval process).
- `make_submission_zip.sh`: builds the single ZIP and refuses a missing or badly named PDF.
- `experiments/`: evidence for the evaluation table in Question 1 Part (a), and a check that the Question 2 knowledge base derives the stated answers. Not part of the submission.
- `question_source/`: the assignment brief.

## Before submitting

1. Run the notebook, play one real game in the last cell, and save it. The two earlier games are scripted.
2. Put every member's PDF in a `pdfs` folder, each named with that member's BITS ID.
3. Build the ZIP, giving the number of members: `./make_submission_zip.sh 4 pdfs`
4. Check that the ZIP holds the notebook plus one PDF per member, as the whole group is responsible for this.
5. One person uploads the single ZIP to Taxila. A missing PDF means no Question 2 marks for that member, and email submissions are not accepted.

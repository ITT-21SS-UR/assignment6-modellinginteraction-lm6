## Goal

The goal of this study was to compare a users actual task completions times, with task the task completion times suggested by the klm-model. Therefore, we designed 4 tasks which the user had to comeplete and log the times he needed to do so. We also calculated the task time the klm-model expected by using its default klm-values and our own klm-values(which we retrieved from another test), for the given tasks.

### Our alternative hypotheses was “Participants that use our enhanced keyboard input with autocompletion can enter text faster than with unenhanced keyboard input” while our null hypothesis stated that ### there was no difference between both conditions or using autocompletion would even lead to slower text input. The application was created with Qt Designer [1] and implemented in Python with the PyQt-Framework [2].

## Experiment Design

We used a within-subjects design with four conditions/tasks. The tasks were counterbalanced for each participant with a balanced latin square.

At the beginning of the experiment the current user was asked to make sure that he was in an undisturbed place for the time of this study so he would be able to fully concentrate on the task. He was also asked to only use 1 hand during the whole experiment. The user was shown the task instruction on the screen. He could take all the time he needed to understand the task. Below the instruction was a "start"-button. As soon as the user clicked on the button, the trial for the first task started. The user was presented with a calculator on which he could fullfill his task. If the User made a mistake he could restart the task by pressing the "Clear"-button with his mouse. After clicking on the "="-button or pressing enter on his keyboard, the task was finished and the next task instruction was displayed, if there was another task for the current participant, or the application closed, if there was not.

The 4 tasks where:

- adding the numbers from 1 to 20 using only the mouse
- adding the numbers from 1 to 20 using only the keyboard
- calculating the result of (3*3 + 4*4) ∗ 15.2 using only the mouse.
- calculating the result of (3*3 + 4*4) ∗ 15.2 using only the keyboard.

We logged the values [timeStamp,eventType,isMouse,klmId,argument] of the following events:
- Input events (had all values filled out):
    - mouseMove: every time the mouse was moved over a new button
    - mouseClick: every time the user clicked on a button with his mouse
    - keystroke: all keystrokes that were allowed in the calculator
- Task events (isMouse, klmId were empty, argument was the current task-identifier):
    - task_started: when the participant pressed the "start"-button
    - task_restarted: when  the participant clicked the "clear"-button
    - task_finished: when the participant clicked the "="-button or pressed enter on his keyboard



Our dependent variable was the time, which the user needed to fullfill a task. We were able to calculate it with help of the timestamps of our logged events. Our independent variable was the task the participant had to do.

We applied counterbalancing to migitate learning effects.


## Participants

The study was conducted by 8 participants ranging in age from 22 to 27 years (m = 24,5, sd = 2,5). All participants were male and studied media informatics at the University of Regensburg. 

## Limitations

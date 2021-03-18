import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import re

helpdialog = '''Type Text to automatically generate a Concordance!

Click the buttons on to the right to highlight all found words!
Features:
-Support for words with Dashes and Apostrophes.
-Ensure's words aren't part of larger words I.e 'Hi' vs 'Hire'.
-Using only built in python modules.
-Decent UI that will automatically stretch to any screen!

Let me know if you're able to break it without using special characters!
'''

infodialog = '''Made By: Sheldon Curtiss
Contact info: SheldonCurtiss@gmail.com
'''


# Handles Logic for when one of the 'output' buttons is pressed.
def ButtonClick(pattern, tag, lines, textswap):
    ClearHighlights()

    # Create Highlight for text
    UIInputField.tag_config("highlight", background="black", foreground="red")

    for wordinstance in re.finditer(rf'{pattern}', textswap):
        # Count amount of line breaks before text was found
        # Count characters from last line break
        # We need to figure out the line the starts on and character on said line.
        
        textbefore = textswap
        textbefore = textbefore[:wordinstance.start()]
        linebreaksbefore = str((textbefore.count('\n')+1))
        textbefore = textbefore.split('\n')
        textbefore = textbefore[-1]
        textbefore = len(textbefore)

        UIInputField.mark_set("matchStart", linebreaksbefore + "." + str(textbefore))
        UIInputField.mark_set("matchEnd", linebreaksbefore + "." + str(textbefore + len(pattern)))
        UIInputField.tag_add(tag, "matchStart", "matchEnd")

    # Create Highlight for Lines
    UILineLabels.tag_config("highlight", background="black", foreground="red")

    # Line Highlighting Logic
    UILineLabels.mark_set("matchStart", "1.0")
    UILineLabels.mark_set("matchEnd", "1.0")
    UILineLabels.mark_set("searchLimit", "end")

    LineCount = tk.IntVar()
    for line in lines:
        while True:
            LineIndex = UILineLabels.search("( " + line + "\\.\n)", "matchEnd", "searchLimit", count=LineCount, regexp=True)
            if LineIndex == "": break
            if LineCount.get() == 0: break
            UILineLabels.mark_set("matchStart", LineIndex)
            UILineLabels.mark_set("matchEnd", "%s+%sc" % (LineIndex, LineCount.get()))
            UILineLabels.tag_add(tag, "matchStart", "matchEnd")

# Info menu super basic
def InfoClick():
    UIInputField.delete('1.0', 'end')
    UIInputField.insert(tk.END, infodialog)

# Help menu super basic
def HelpClick():
    UIInputField.delete('1.0', 'end')
    UIInputField.insert(tk.END, helpdialog)


# Logic for wiping existing highlights
def ClearHighlights():
    # Clear Existing highlighted words
    for ExistingHighlight in UIInputField.tag_names():
        UIInputField.tag_delete(ExistingHighlight)

    # Clear Existing highlighted lines
    for ExistingHighlight in UILineLabels.tag_names():
        UILineLabels.tag_delete(ExistingHighlight)

# Logic for Clearing existing buttons
def ClearButtons():
    # Wipes all existing buttons.
    if len(UIOutputButtons) >= 1:
        for UIOutputButton in UIOutputButtons:
            UIOutputButton.destroy()

# Creates a button that serves as our output as well as for use with highlighting
def CreateButton(frame, buttonlabel, buttonword, foundlines, cleanedtext):
    ButtonObject = tk.Button(frame, text=buttonlabel, width=50, command=lambda: ButtonClick(buttonword, "highlight", lines=foundlines, textswap=cleanedtext))
    ButtonObject.pack(side="top")
    return ButtonObject

# Triggers whenever Typing has stopped.
def GenerateConcordance(event):
    ClearHighlights()
    ClearButtons()

    enteredtext = UIInputField.get("1.0", "end")

    # Some of the logic here.
    # A placeholder lower version of the inputted text
    checktext = enteredtext.lower()

    # Input text is lowered, linebreaks are removed so split can function, then numbers and symbols not found in words are removed.
    processedtext = enteredtext.lower()
    processedtext += ' '
    processedtext = processedtext.replace('\n', ' ')
    processedtext = re.sub("[^a-zA-Z' -]", '', processedtext)
    processedtext = processedtext.split()
    processedtext.sort(key=str.lower)

    # Where we store our already checked words
    processedwords = []
    for Word in processedtext:
        if Word not in processedwords:
            processedwords.append(Word)
            WordCount = processedtext.count(Word)
            UIOutputButtonLabel = Word + ': {' + str(WordCount) + ':'

            processedchecktext = checktext

            # Logic to ensure we don't accidentally count 'coolest' when looking for the word 'cool'
            checktextWordFragments = re.findall(rf"(?:[a-zA-Z'-]+{Word}[a-zA-Z'-]+|[a-zA-Z'-]+{Word}|{Word}[a-zA-Z'-]+)", processedchecktext)
            Iteration = 1
            for Fragment in checktextWordFragments:
                garbagetext = ''
                for letter in range(len(Fragment)):
                    garbagetext += '-'

                Iteration += 1

                processedchecktext = processedchecktext.replace(Fragment, garbagetext)


            # Logic for determining line positions - We search through the input text and count linebreaks upwards.
            WordLocationFinder = re.findall(rf"(?:[\S\s]*?{Word}|{Word})", processedchecktext, flags=re.MULTILINE)
            CurrentLine = 1
            foundlines = []
            for WordLocation in WordLocationFinder:
                CurrentLine += WordLocation.count('\n')


                foundlines.append(str(CurrentLine))


                UIOutputButtonLabel += str(CurrentLine) + ','
            UIOutputButtonLabel = UIOutputButtonLabel[:-1]
            UIOutputButtonLabel += '}'

            # Here we send off the button to be created and add the button to our array for next clear.
            ButtonObject = CreateButton(UIRightFrame, UIOutputButtonLabel, Word, foundlines, processedchecktext)
            UIOutputButtons.append(ButtonObject)


# UI setup - Everything should stretch to any resolution with no problems.
UIOutputButtons = []

root = tk.Tk()
UILeftFrame = tk.Frame(root)
UILeftFrame.pack(side='left', expand='True', fill='both')

UIRightFrame = tk.Frame(root)
UIRightFrame.pack(side='top')

UIInfoFrame = tk.Frame(UIRightFrame)
UIInfoFrame.pack(side='right')

UIInputLabel = tk.Label(UILeftFrame, text="Input", height=1, width=10)
UIInputLabel.pack(side="top")

UIOutputLabel = tk.Label(UIRightFrame, text="Output", height=1, width=10)
UIOutputLabel.pack(side="top")

UIInfoLabel = tk.Label(UIInfoFrame, text="Info", height=1, width=50)
UIInfoLabel.pack(side="top")

# Here we generate our fancy line labels
LabelCounter = 1
UILineLabelText = ''
while LabelCounter <= 200:
    UILineLabelText += ' ' + str(LabelCounter) + '.\n'
    LabelCounter += 1

# Line Label holder
UILineLabels = tk.Text(UILeftFrame, height=1, width=4)
UILineLabels.pack(side="left", expand='False', fill='y')
UILineLabels.insert(tk.END, UILineLabelText)
UILineLabels['state'] = tk.DISABLED

# Our main text input field, which we monitor when typing stops.
UIInputField = ScrolledText(UILeftFrame)
UIInputField.pack(side="top", expand='True', fill='both')
UIInputField.insert(tk.END, 'Type here!')
UIInputField.bind('<KeyRelease>', GenerateConcordance)

# Filler space
UIOutputPadding = tk.Label(UIRightFrame, text="", height=1, width=50)
UIOutputPadding.pack(side="top")

# Top Bar
root.title("The Ultimate Concordance Application By: Sheldon Curtiss")

UIInfoButton = tk.Button(UIInfoLabel, text="☕", width=5, command=lambda: InfoClick())
UIInfoButton.pack(side="top")

UIHelpButton = tk.Button(UIInfoLabel, text="❔", width=5, command=lambda: HelpClick())
UIHelpButton.pack(side="top")

# Main Loop
tk.mainloop()

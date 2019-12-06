#!/usr/bin/env python3
import subprocess
import json
import argparse
import sys

class lesson:
    #initialize the salient parts of each lesson
    def __init__(self, title = "", objectives = [], plan = [], is_topic = True, continue_topic = False, id = "Undefined"):
        self.lesson_number = "Undefined"  #default - actual number will be set once the lesson is part of a unit
        self.title = title
        self.objectives = objectives
        self.plan = plan
        self.is_topic = is_topic
        self.continue_topic = continue_topic
        self.id = id
        self.count_within = 1

    def generate_pdf_string(self):
        return r'''% Automatically generated lesson plan file
% Do not modify - all changes will be overwritten

\documentclass{{article}}

\input{{../generalCourse}}
\input{{info/generalUnit}}
\input{{info/objectives}}

\usepackage{{mathgeneral}}
\usepackage[margin = 1in, letterpaper]{{geometry}}
\usepackage{{framed}}
\usepackage{{titling}}
\usepackage{{enumitem}}
\usepackage{{amsfonts}}

\newcommand{{\lessonNum}}{{{ln}}}
\title{{{0}}}

\begin{{document}}

{{\Huge \noindent \thetitle}} \par \vspace{{\baselineskip}}
\noindent\course \hspace{{\stretch{{1}}}} \textbullet \hspace{{\stretch{{1}}}} Lesson~\lessonNum{{}} \hspace{{\stretch{{1}}}} \textbullet \hspace{{\stretch{{1}}}} \unit 

\noindent\hrulefill


\section*{{Objectives}}
\begin{{framed}}
    \objectives{id}
\end{{framed}}


\section*{{Plan}}
\begin{{itemize}}
    {plan}
\end{{itemize}}

\end{{document}}
        '''.format(self.get_formatted_title(), self.objectives, plan = r'''\item[]''' if self.plan == [] else "\\item " + "\n\\item ".join(self.plan), ln = self.lesson_number, id = self.id)

    def generate_objectives_command(self):
        r'''
        Returns a command that prints the objectives of a lesson

        If there are objectives, each one will be specified in a separate \item and the entire set of objectives will be typeset into some kind of itemize environment
        If there are no objectives, then the command will just be blank (but still exist)
        '''

        if self.objectives == "":
            return r'''\providecommand{{\objectives{id}}}{{}}'''.format(id = self.id)
        else:
            return r'''\providecommand{{\objectives{id}}}{{%
\begin{{itemize}}[noitemsep, topsep=0pt]
    {items}
\end{{itemize}}
}}'''.format(id=self.id, items="\\item " + "\n\\item ".join(self.objectives))

    def get_formatted_title(self):
        if self.is_topic == True:
            return "Topic {0} - ".format(self.topic_number) + self.title
        else:
            return self.title

    def set_lesson_number(self, num):
        self.lesson_number = num
    def set_topic_number(self, num):
        self.topic_number = num

    def generate_tex(self):
        ln_string = str(self.lesson_number).rjust(2, "0")
        file_name = "lp-" + ln_string + ".tex"

        with open(file_name, "w") as file:
            file.write(self.generate_pdf_string())
        print("Wrote", file_name)



class unit_lps:
    def __init__(self, *lessons):
        current_topic_number = 0 #current topic - will increment depending on lessons
        self.lessons = []
        for n, l in enumerate(lessons):
            #print(n + 1) #for debugging
            l.set_lesson_number(n + 1)
            
            if l.is_topic == True and l.continue_topic == False:
                current_topic_number += 1
            l.set_topic_number(current_topic_number)

            self.lessons.append(l)

        self.json_file = "test.json"

    def display_topics(self):
        print("{0:<13} {1}".format("Lesson Number", "Title"))
        for l in self.lessons:
            print("{0:<13} {1}".format(l.lesson_number, l.title))

    def generate_tex(self):
        print("Beginning to write files")
        for l in self.lessons:
            l.generate_tex()
        print("Done writing files")

    def duplicate_ids(self):
        ids = []
        duplicates = []
        for l in self.lessons:
            ids.append(l.id)

        for i in ids:
            if ids.count(i) > 1 and i not in ids:
                duplicates.append(i)

        return duplicates


    # JSON stuff

    def set_json_file(self, file_name):
        self.json_file = file_name

    def encode_unit_lps(self):
        pass


    def generate_json(self):
        with open(self.json_file, "w") as write_file:
            json.dump(self, write_file, indent = 4)



# JSON stuff
def encode_lesson(l):
    '''
    returns a dictionary representing the lesson
    '''
    lesson_dict = {
            "__lesson__": True,
            "title": l.title,
            "objectives": l.objectives,
            "plan": l.plan,
            "is_topic": l.is_topic,
            "continue_topic": l.continue_topic,
            "id": l.id
            }
    return lesson_dict

def decode_lesson_json(dct):
    if "__lesson__" in dct:
        return lesson(dct["title"], dct["objectives"], dct["plan"], dct["is_topic"], dct["continue_topic"], dct["id"])
    else:
        return dct



################### Main Program #################

parser = argparse.ArgumentParser(description = 'Generate a set of lesson plan files from lessons stored as JSON')
parser.add_argument('lessons_file', type=str, help = 'JSON file which contains a single list of all of the lessons to be processed')
parser.add_argument('--generate_objectives', action='store_true', help = 'Generate a file containting a LaTeX command containing the objectives for each lesson')
parser.add_argument('--objectives_file', type=str, action='store', default='info/objectives.tex', help = 'Destination file for objectives')
parser.add_argument('--generate_blank', type = int, default = None, help = 'Generates a blank unit with the specified number of lessons')
args = parser.parse_args()

# First test to see if we are generating a blank file or reading an already created on
if args.generate_blank != None:
    lessons_list = [lesson() for i in range(args.generate_blank)]
    unit = unit_lps(*lessons_list)
    with open(args.lessons_file, "w") as f:
        json.dump(unit.lessons, f, default = encode_lesson, indent = 4, sort_keys = True)
        print("Wrote to {}".format(args.lessons_file))
    sys.exit(0)

with open(args.lessons_file, "r") as f:
    test = json.load(f, object_hook = decode_lesson_json)

unit = unit_lps(*test)

#Check to ensure that all ids are unique
if unit.duplicate_ids() != []:
    print("Duplicate ids detected! Duplicate ids are: ")
    for i in unit.duplicate_ids():
        print(i)
    sys.exit(1)

#print("generate_objectives:", args.generate_objectives)

if args.generate_objectives == True:
    to_write = "% Automatically generated commands corresponding to objectives for different lessons\n% Do not edits - all changes will be overwritten\n"
    for l in unit.lessons:
        to_write += l.generate_objectives_command() + "\n"

    with open(args.objectives_file, "w") as f:
        f.write(to_write)
        print("Wrote objectives to", args.objectives_file)


else:
    unit.generate_tex()

#!/usr/bin/env python3
import subprocess
import json
import yaml
import argparse
import sys

########### Miscellaneous Functions for Utility

#Shamelessly stolen from https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
def int_to_roman(input):
    """ Convert an integer to a Roman numeral. """
    if not isinstance(input, type(1)):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)




########### lesson and unit classes + functions associated with them

class lesson:
    #initialize the salient parts of each lesson
    def __init__(self, title = "", objectives = None, plan = None, is_topic = True, is_continuation = False, id = "Undefined", count_within = None):
        self.lesson_number = "Undefined"  #default - actual number will be set once the lesson is part of a unit
        self.title = title
        self.objectives = objectives
        self.plan = plan
        self.is_topic = is_topic
        self.is_continuation = is_continuation
        self.id = id
        self.count_within = count_within #This counts if it is part of a sequence of lessons (part 1, part 2, &c.)

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
        '''.format(self.get_formatted_title(), self.objectives, plan = r'''\item[]''' if (self.plan == [] or self.plan == None) else "\\item " + "\n\\item ".join(self.plan), ln = self.lesson_number, id = self.id)

    def generate_objectives_command(self):
        r'''
        Returns a command that prints the objectives of a lesson

        If there are objectives, each one will be specified in a separate \item and the entire set of objectives will be typeset into some kind of itemize environment
        If there are no objectives, then the command will just be blank (but still exist)
        '''

        if self.objectives in ["", None]:
            return r'''\providecommand{{\objectives{id}}}{{}}'''.format(id = self.id)
        else:
            return r'''\providecommand{{\objectives{id}}}{{%
\begin{{itemize}}[noitemsep, topsep=0pt]
    {items}
\end{{itemize}}
}}'''.format(id=self.id, items="\\item " + "\n\\item ".join(self.objectives))

    def get_formatted_title(self):
        title = ''
        if self.is_topic == True:
            title += "Topic {0} --- ".format(self.topic_number) 
        title += self.title
        if self.count_within != None:
            title += ' --- Part {}'.format(int_to_roman(self.count_within))

        return title

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
            
            if l.is_topic == True and l.is_continuation == False:
                current_topic_number += 1
            l.set_topic_number(current_topic_number)

            self.lessons.append(l)

        '''Now go through and  muck with the parts of a lesson
        For each lesson (except the first --- it can't be a continuation!) see if it is a continuation. If it is, check if the count_within property of the previous lesson is set; if not, set that to 1. In either case, set your own count_within property to one more than the previous one.'''
        for i in range(1, len(self.lessons)):
            current = self.lessons[i]
            prev = self.lessons[i - 1]
            if current.is_continuation:
                if prev.count_within == None:
                    prev.count_within = 1
                current.count_within = prev.count_within + 1

                #now reset
                self.lessons[i - 1] = prev
                self.lessons[i] = current


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



# Switching between the lesson object and dictionaries
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
            "is_continuation": l.is_continuation,
            "id": l.id,
            "count_within": l.count_within
            }
    return lesson_dict

def decode_lesson(dct):
    '''
    Takes in a dictionary and returns the equivalent lesson
    '''
    if "__lesson__" in dct:
        return lesson(dct["title"], dct["objectives"], dct["plan"], dct["is_topic"], dct["is_continuation"], dct["id"], dct.get("count_within", None))
    else:
        print("Error converting to lesson")
        return dct



################### Main Program #################

parser = argparse.ArgumentParser(description = 'Generate a set of lesson plan files from lessons stored as YAML')
parser.add_argument('lessons_file', type=str, help = 'YAML file which contains a single list of all of the lessons to be processed')
parser.add_argument('--generate_objectives', action='store_true', help = 'Generate a file containting a LaTeX command containing the objectives for each lesson')
parser.add_argument('--objectives_file', type=str, action='store', default='info/objectives.tex', help = 'Destination file for objectives')
parser.add_argument('--generate_blank', type = int, default = None, help = 'Generates a blank unit with the specified number of lessons')
args = parser.parse_args()

# First test to see if we are generating a blank file or reading an already created on
if args.generate_blank != None:
    lessons_list = [lesson() for i in range(args.generate_blank)]
    unit = unit_lps(*lessons_list)
    unit_to_convert = [encode_lesson(l) for l in unit.lessons]
    with open(args.lessons_file, "w") as f:
        yaml.dump(unit_to_convert, f, default_flow_style = False)
        print("Wrote to {}".format(args.lessons_file))
    sys.exit(0)

with open(args.lessons_file, "r") as f:
    test = yaml.safe_load(f)
    all_lessons = [decode_lesson(d) for d in test]

#Is it actually converting correctly?
#for l in test:
#    print(l)

unit = unit_lps(*all_lessons)

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

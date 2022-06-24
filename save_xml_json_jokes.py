import time
from typing import List, Tuple, Dict
import re
import random
import csv
from lxml import etree
import json


class Joke:
    """The Joke object contains the joke, and some metadata on that joke. One can compare the jokes by upvotes"""

    def __init__(self, raw_joke):
        self.raw_joke = raw_joke
        self.author = self.raw_joke[0]
        self.link = self.raw_joke[1]
        self.joke = self.raw_joke[2]
        self.rating = int(self.raw_joke[3])
        self.time = self.raw_joke[4]

        self.sentences_joke = self.split_into_sentences()
        self.tokenized_joke = self._tokenize()
        self.filtered_joke = self.filter_profanity()[0]
        self.num_profanities = self.filter_profanity()[1]

        # TODO: Save representations in xml and json
        self.xml_print = self._get_xml_repr()
        self.json_print = self._get_json_repr()

    def split_into_sentences(self) -> List[str]:
        """Split text into sentences"""
        output = re.findall(r' ?([^.!?\n]+[.?!]*|\n)', self.joke)
        return output

    def _tokenize(self) -> List[List[str]]:
        """Tokenize all the words in the sentences"""
        output = []
        for sentence in self.sentences_joke:
            tokenized_sentence = re.findall(r'([\w\']+|\?|\.|\n|,|!)', sentence)
            output.append(tokenized_sentence)
        return output

    def filter_profanity(self, filename="profanities.txt") -> Tuple[List[List[str]], int]:
        """Filter out all the profanity"""

        output = []

        # Count number of profanities
        num_profanities = 0

        # Read in profanity file
        with open(filename, "r", encoding='utf-8') as file:
            profanities = file.read().split("\n")

        for sentence in self.tokenized_joke:
            no_profanity = True
            text_sentence = " ".join(sentence)
            for profanity in profanities:

                # Check if there is profanity in the sentence
                if profanity in text_sentence:
                    profanity_in_text = True
                else:
                    profanity_in_text = False

                while profanity_in_text:
                    num_profanities += 1
                    no_profanity = False

                    # Find the index of the profanity
                    index = text_sentence.index(profanity)
                    front = text_sentence[:index - 1]

                    # Find the words that need to be replaced
                    num_words_before_profanity = len(front.split(" "))
                    num_profanity_words = len(profanity.split(" "))
                    profanity_in_sentence = sentence[
                                            num_words_before_profanity: num_words_before_profanity + num_profanity_words]

                    # Replace the profanity with '#'
                    replacement = ["#" * len(word) for word in profanity_in_sentence]

                    # Construct new sentence composed of the parts with and without profanity
                    new_sent = []
                    new_sent.extend(sentence[:num_words_before_profanity])
                    new_sent.extend(replacement)
                    new_sent.extend(sentence[num_words_before_profanity + len(replacement):])
                    text_sentence = " ".join(new_sent)
                    sentence = new_sent

                    # Check if there is still profanity in the sentence
                    if profanity in text_sentence:
                        profanity_in_text = True

                    else:
                        profanity_in_text = False
                        output.append(new_sent)

            # Add sentence immediately if there are no profanities in the sentence
            if no_profanity:
                output.append(sentence)
        return output, num_profanities

    def tell_joke(self):
        if len(self.filtered_joke) > 1:
            build_up = self.filtered_joke[:-1]
            punch_line = self.filtered_joke[-1:]

            print(self.pretty_print(build_up))
            time.sleep(1)
            print(self.pretty_print(punch_line))
        else:
            print(self.pretty_print(self.filtered_joke))

    @staticmethod
    def pretty_print(joke) -> str:
        """Print in a humanly readable way"""
        output = ""
        for sentence in joke:
            output += " ".join(sentence) + " "
        return output

    # TODO: Implement the method
    def _get_xml_repr(self) -> etree.Element:
        """Get the xml representation of the Joke with all its attributes as nodes"""
        # Create the attributes
        joke_xml = etree.Element('joke')
        text = etree.SubElement(joke_xml, "text")
        author = etree.SubElement(joke_xml, "author")
        link = etree.SubElement(joke_xml, "link")
        score = etree.SubElement(joke_xml, "score")
        time = etree.SubElement(joke_xml, "time")
        profanity_score = etree.SubElement(joke_xml, "profanity_score")
        text.text = self.joke
        author.text = self.author
        link.text = self.link
        score.text = str(self.rating)
        time.text = self.time
        profanity_score.text = str(self.num_profanities)
        joke_str = etree.tostring(joke_xml, encoding='unicode')

        return joke_xml

    def _get_json_repr(self) -> Dict:

        # Create a dictionary that contains all the attributes as key:value pair
        all_data = {
            "author": self.author,
            "link": self.link,
            "text": self.joke,
            "rating": self.rating,
            "time": self.time,
            "profanity_score": self.num_profanities
        }
        return all_data


    def __repr__(self):
        """Allows for printing"""
        return self.pretty_print(self.filtered_joke)

    def __eq__(self, other):
        """Equal rating"""
        return self.rating == other.rating

    def __lt__(self, other):
        """less than rating"""
        return self.rating > other.rating

    def __gt__(self, other):
        """greater than rating"""
        return self.rating < other.rating

    def __le__(self, other):
        """less than or equal rating"""
        return self.rating >= other.rating

    def __ge__(self, other):
        """greater than or equal rating"""
        return self.rating <= other.rating


class JokeGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.joke_objects = self.make_jokes_objects()


    def make_jokes_objects(self):

        # if filename endswith .json execute this statement
        if self.filename.endswith('.json'):
            list_objects = []
            big_list = []
            # open the file and read the file
            with open(self.filename, "r", encoding='utf-8') as lines:
                jokes = json.load(lines)

                for i in jokes.values():
                    # enter the value-dimension which contains all the values of each joke
                    for val in i.values():
                        # append all the values to a list
                        list_objects.append(val)
                    # append the values-list to a first-dimension list
                    big_list.append(list_objects)

                    # Pass each row to the Joke Class and create Joke Objects
                    jokes = [Joke(row) for row in big_list]


        # else read a csv file and pass it to the Joke Class
        else:
            with open(self.filename, "r", encoding='utf-8') as lines:
                lines = csv.reader(lines, delimiter=',')
                jokes = [Joke(row) for row in lines]

        return jokes

    def generate_jokes(self):
        for joke in self.jokes:
            if len(joke.filtered_joke) > 1:
                joke.tell_joke()
            time.sleep(10)

    def random_joke(self):
        joke = random.sample(self.jokes, 1)[0]
        joke.tell_joke()


    def save_jokes_xml(self, outfile: str) -> None:
        """Save all the jokes of the Generator in their xml representation to the outfile"""

        # Create the superelement 'jokes'
        jokes = etree.Element("jokes")

        # goes through every joke object
        for joke in self.joke_objects:
            # every XML node from the class Joke should be appended to the superelement
            jokes.append(joke.xml_print)

        # Create an XML-file
        final_xml = etree.ElementTree(jokes)
        final_xml.write('reddit_dadjokes.xml', pretty_print=True)


    def save_jokes_json(self, outfile: str) -> None:
        """Save all the jokes of the Generator in their json representation to the outfile"""

        i = 1
        # create first dimension that contains indices
        json_dict = {}

        # Enter the joke-objects dimension
        for joke in self.joke_objects:
            # the key accesses the variable that consists of all the JSON-Formatted jokes
            json_dict[i] = joke.json_print
            # print(joke.json_print)
            # increase indices
            i += 1

        # Create a JSON-Object
        json_dump = json.dumps(json_dict, indent=3)

        # Create JSON-File as an output
        with open("reddit_dadjokes.json", "w") as output:
            output.write(json_dump)


if __name__ == "__main__":
    # You can use the following commands for testing your implementation
    gen = JokeGenerator("reddit_dadjokes.csv")
    gen.save_jokes_xml('reddit_dadjokes.xml')
    # gen = JokeGenerator('example.json')
    gen.save_jokes_json('reddit_dadjokes.json')
    # gen.JokeGenerator("reddit_dadjokes.json")

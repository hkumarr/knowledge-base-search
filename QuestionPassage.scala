package org.allenai.ari.controller.questionparser

import org.allenai.common.Resource
import org.allenai.nlpstack.segment.defaultSegmenter
import scopt.OptionParser
import spray.json._

import java.io.File

/** A data structure representing a "question passage," consisting of a "prologue," a
  * "question," and a set of "choices." For instance, the multiple choice question:
  *
  * "Alice has 5 apples. She gives 2 apples to Bob. What is an apple? (A) a fruit (B) a veggie"
  *
  * would have the following representation:
  * - prologue: Seq("Alice has 5 apples.", "She gives 2 apples to Bob.")
  * - question: "What is an apple?"
  * - choices: Map("A" -> "a fruit", "B" -> "a veggie")
  *
  * @param prologue a sequence of strings giving the question prologue
  * @param question the main question of the passage
  * @param choices a map from choice keys to corresponding choice text
  */
case class QuestionPassage(prologue: Seq[String], question: String,
  choices: Map[String, String])

private case class QuestionPassageConfig(
  inputFilename: String = "",
  fitbFilename: String = ""
)

object QuestionPassage {

  /** A toy command-line tool for processing raw question passages, one per line.
    *
    * Usage: QuestionPassage [options]
    *
    * -i <file> | --input <file>
    * the file containing the question passages (one per line)
    *
    * @param args command-line arguments (see above)
    */

  def main(args: Array[String]) {
    val optionParser = new OptionParser[QuestionPassageConfig]("QuestionPassage") {
      opt[String]('i', "input") required () valueName ("<file>") action { (x, c) =>
        c.copy(inputFilename = x)
      } text ("the file containing the question passages" +
        " (one per line)")
      opt[String]('g', "generator") valueName ("<file>") action { (x, c) =>
        c.copy(fitbFilename = x)
      } text ("the file containing the serialized fill-in-the-blank generator")
    }
    val clArgs: QuestionPassageConfig = optionParser.parse(args, QuestionPassageConfig()).get
    val source = scala.io.Source.fromFile(clArgs.inputFilename)
   
    /** Change the file path to your current folder to where the question file resides
    */
    val pw = new java.io.PrintWriter(new File("/home/harish/NLP_Aristo/aristo/blank_statements.txt"))
    val fitbGenerator =
      if (clArgs.fitbFilename == "") {
        FillInTheBlankGenerator.mostRecent
      } else {
        FillInTheBlankGenerator.load(clArgs.fitbFilename)
      }
    for (line <- source.getLines()) {
      val qpassage = QuestionPassage.createPassage(line, Set(
        SquareBracketedChoiceIdentifier,
        ParentheticalChoiceIdentifier
      ))
      println("---")
      pw.write("---"+"\n")
      println(qpassage.question)
      pw.write(qpassage.question+"\n")
      val question = Question.constructFromString(qpassage.question)
      fitbGenerator.generateFITB(question) match {
        case Some(fitb) =>  pw.write(fitb.text+"\n")
        case None => {println("***Generation failure ***")
		pw.write("***Generation failure ***"+"\n")
	}
      }
    }
    source.close()
  }

  /** Processes a raw string and converts it to a QuestionPassage object.
    *
    * This method takes a set of ChoiceIdentifiers (see ChoiceIdentifier.scala) as its
    * second argument. It will call the .apply operator of each ChoiceIdentifier and then take
    * the result of the most "successful" one (where success is defined as the size of the choice
    * map it returns).
    *
    * @param passageStr the raw text of the passage
    * @param choiceIdentifiers a set of ChoiceIdentifiers
    * @return the constructed QuestionPassage object
    */
  def createPassage(
    passageStr: String,
    choiceIdentifiers: Set[ChoiceIdentifier]
  ): QuestionPassage = {

    val choiceIdentifications = choiceIdentifiers map { choiceIdentifier =>
      choiceIdentifier(passageStr)
    }
    val (questionText, choiceMap) = choiceIdentifications maxBy { ident => ident._2.size }
    val questionSegments: Seq[String] =
      defaultSegmenter.segment(questionText).toSeq.reverse map { _.text }
    QuestionPassage(questionSegments.tail.reverse, questionSegments.head, choiceMap)
  }
}

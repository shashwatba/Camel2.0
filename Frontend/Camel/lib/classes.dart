class Question {
  final String question;
  final String choice1;
  final String choice2;
  final String choice3;
  final String choice4;
  final String correct;
  final String keyword;
  final String difficulty;

  Question({
    required this.question,
    required this.choice1,
    required this.choice2,
    required this.choice3,
    required this.choice4,
    required this.correct,
    required this.keyword,
    required this.difficulty,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      question: json['question'] ?? '',
      choice1: json['choice1'] ?? '',
      choice2: json['choice2'] ?? '',
      choice3: json['choice3'] ?? '',
      choice4: json['choice4'] ?? '',
      correct: json['correct'] ?? '',
      keyword: json['keyword'] ?? '',
      difficulty: json['difficulty'] ?? '',
    );
  }
}


class UserAnswer {
  final String questionId;
  final String answer;

  UserAnswer({required this.questionId, required this.answer});

  factory UserAnswer.fromJson(Map<String, dynamic> json) {
    return UserAnswer(
      questionId: json['questionId'] ?? '',
      answer: json['answer'] ?? '',
    );
  }
}

class SavedQuiz {
  final String quizId;
  final String topic;
  final String keyword;
  final List<Question> questions;
  final List<UserAnswer> userAnswers;
  final String generatedAt;
  final String? completedAt;
  final int? score;
  final int totalQuestions;

  SavedQuiz({
    required this.quizId,
    required this.topic,
    required this.keyword,
    required this.questions,
    required this.userAnswers,
    required this.generatedAt,
    this.completedAt,
    this.score,
    required this.totalQuestions,
  });

  factory SavedQuiz.fromJson(Map<String, dynamic> json) {
    var questionsJson = json['questions'] as List<dynamic>? ?? [];
    var userAnswersJson = json['user_answers'] as List<dynamic>? ?? [];

    return SavedQuiz(
      quizId: json['quiz_id'] ?? '',
      topic: json['topic'] ?? '',
      keyword: json['keyword'] ?? '',
      questions: questionsJson.map((q) => Question.fromJson(q)).toList(),
      userAnswers: userAnswersJson.map((a) => UserAnswer.fromJson(a)).toList(),
      generatedAt: json['generated_at'] ?? '',
      completedAt: json['completed_at'],
      score: json['score']??0,
      totalQuestions: json['total_questions'] ?? 0,
    );
  }
}

class QuizHistoryResponse {
  final List<SavedQuiz> quizzes;
  final int totalCount;

  QuizHistoryResponse({required this.quizzes, required this.totalCount});

  factory QuizHistoryResponse.fromJson(Map<String, dynamic> json) {
    var quizzesJson = json['quizzes'] as List<dynamic>? ?? [];

    return QuizHistoryResponse(
      quizzes: quizzesJson.map((q) => SavedQuiz.fromJson(q)).toList(),
      totalCount: json['total_count'] ?? 0,
    );
  }
}

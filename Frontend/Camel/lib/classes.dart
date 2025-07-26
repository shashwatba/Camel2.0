class Question {
  final String id;
  final String text;

  Question({required this.id, required this.text});

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['id'] ?? '',
      text: json['text'] ?? '',
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
      score: json['score'],
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

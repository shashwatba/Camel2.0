import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:camel/classes.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'GPT Knowledge DB',
      theme: ThemeData.light().copyWith(

        scaffoldBackgroundColor: Color(0xFFF9FAFB),
        cardColor: Colors.white,
        dividerColor: Colors.grey.shade300,
        textTheme: ThemeData.light().textTheme.apply(
          bodyColor: Colors.black87,
          displayColor: Colors.black87,
          fontFamily: 'Poppins',
        ),
        chipTheme: ChipThemeData(
          backgroundColor: Colors.grey.shade200,
          labelStyle: TextStyle(color: Colors.black87),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          side: BorderSide(color: Colors.grey.shade400),
          secondaryLabelStyle: TextStyle(color: Colors.black54),
          brightness: Brightness.light,
          deleteIconColor: Colors.black54,
          disabledColor: Colors.grey.shade300,
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        ),
      ),
      home: DashboardScreen(),
      //home: CenteredLandingPage(),
    );
  }
}

class DashboardScreen extends StatefulWidget {

  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ScrollController _scrollController = ScrollController();
  final ScrollController _forgetScrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    _forgetScrollController.dispose();

    super.dispose();
  }

  final List<Map<String, dynamic>> whatYouLearned = [
    {
      'title': 'Fixed Point Combinator',
      'tag': 'Functional Programming',
      'summary': 'Used to express recursion without named functions.\n'
          'In lambda calculus, fixed-point combinators like the Y combinator allow us to define recursive behavior in a language without native support for recursion. '
          'It achieves this by passing a function to itself, enabling a form of self-reference. This concept is foundational in theoretical computer science and functional programming languages.',
      'time': '3 hours ago',
    },
    {
      'title': 'NAS Rising Trend',
      'tag': 'Finance',
      'summary': 'Sharp rise since April 2025 due to AI tech demand surge.\n'
          'The Nasdaq index has been showing a steep upward trend, driven by investor optimism around generative AI and semiconductor sectors. '
          'Companies like NVIDIA, AMD, and large tech firms have seen massive gains due to increased demand for computation and model training infrastructure.',
      'time': '7 hours ago',
    },
  ];

  final List<Map<String, dynamic>> youMightForget = [
    {
      'title': 'Poisson Ratio of NiTi Wire',
      'tag': 'Material Science',
      'summary': 'Important material property in NiTi alloy used in shape memory applications.\n'
          'Poisson’s ratio describes the ratio of lateral contraction to axial elongation in a material under stress. '
          'NiTi (Nitinol) exhibits unique behavior due to its superelastic and shape memory properties, and accurately measuring this ratio is crucial for its biomedical and actuator applications.',
      'time': '12 hours ago',
    },
    {
      'title': 'Lambda Calculus Variable Binding',
      'tag': 'Functional Programming',
      'summary': 'Mechanism of how variables are assigned and scoped in lambda calculus.\n'
          'In lambda calculus, variable binding governs how symbols are associated with values or functions. '
          'It distinguishes between free and bound variables, and this scoping mechanism is key to understanding closures, substitution, and evaluation in functional languages.',
      'time': '1 day ago',
    },
    {
      'title': 'Quant ETF Structure Basics',
      'tag': 'Finance',
      'summary': 'Fundamental concepts of quantitative exchange-traded funds and their structure.\n'
          'Quantitative ETFs use algorithmic models to select and rebalance portfolios based on statistical factors like momentum, value, or volatility. '
          'Understanding their structure involves examining the underlying index rules, execution strategies, and the benefits and risks of rules-based investing.',
      'time': '3 days ago',
    },
    {
      'title': 'Bayesian Networks Basics',
      'tag': 'Machine Learning',
      'summary': 'Probabilistic graphical models representing conditional dependencies.\n'
          'Bayesian Networks use directed acyclic graphs to model probabilistic relationships among variables. '
          'They are useful for reasoning under uncertainty, performing inference, and updating beliefs as new data is observed. Applications include diagnostics, prediction, and decision support.',
      'time': '2 days ago',
    },
    {
      'title': 'YOLO Object Detection',
      'tag': 'Computer Vision',
      'summary': 'Real-time object detection algorithm using a single neural network.\n'
          'YOLO (You Only Look Once) reformulates object detection as a single regression problem, directly predicting bounding boxes and class probabilities. '
          'Unlike two-stage detectors, YOLO is fast and efficient, making it suitable for real-time applications such as surveillance and autonomous driving.',
      'time': '5 hours ago',
    },
    {
      'title': 'Markov Decision Processes',
      'tag': 'Reinforcement Learning',
      'summary': 'Framework for modeling decision making in stochastic environments.\n'
          'An MDP consists of states, actions, transition probabilities, and reward functions. '
          'It provides a mathematical model for agents that learn to make sequences of decisions to maximize long-term reward, laying the foundation for many reinforcement learning algorithms.',
      'time': '10 hours ago',
    },
  ];




  void showCardDetail(BuildContext context, Map<String, String> card) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(card['title']!),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Chip(label: Text(card['tag']!)),
            SizedBox(height: 10),
            Text(card['summary']!),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text('Close'),
          ),
        ],
      ),
    );
  }

  void showSimpleCardDetail(BuildContext context, SavedQuiz card) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        title: Text(
          card.topic,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        content: Container(
          width: 600,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            spacing: 4,
            children: [
              TagContainer(text: card.keyword, isForgot: false),
              SizedBox(height: 10),
              // Summary 강조용 박스
              // Container(
              //   padding: EdgeInsets.all(10),
              //   decoration: BoxDecoration(
              //     color: Colors.yellow[100],
              //     borderRadius: BorderRadius.circular(8),
              //   ),
              // ),

              SizedBox(height: 10),
              Container(
                height: 300,
                child:  ListView.builder(
                  itemCount: card.questions.length,
                  itemBuilder: (context, index) {
                    final question = card.questions[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      elevation: 3,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      color: Colors.white,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "Q${index + 1}: ${question.question ?? ''}",
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 12),
                            ...List.generate(4, (i) {
                              final choices = [question.choice1, question.choice2, question.choice3, question.choice4];
                              final labels = ['A', 'B', 'C', 'D'];
                              final isCorrect = labels[i] == question.correct;

                              return Container(
                                margin: const EdgeInsets.symmetric(vertical: 4),
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                decoration: BoxDecoration(
                                  color: isCorrect ? Colors.green : Colors.grey.shade200,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  "${i + 1}: ${choices[i] ?? ''}",
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w500,
                                    color: isCorrect ? Colors.white : Colors.black87,
                                  ),
                                ),
                              );
                            }),
                          ],
                        ),
                      ),
                    );

                  },
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text('Close'),
          ),
        ],
      ),
    );
  }

  Future<QuizHistoryResponse> fetchQuizHistory() async {
    final url = Uri.parse('http://127.0.0.1:8000/quiz-history');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonBody = jsonDecode(response.body);
      return QuizHistoryResponse.fromJson(jsonBody);
    } else {
      throw Exception('Failed to load quiz history');
    }
  }



  @override
  Widget build(BuildContext context) {
    const sectionTitleStyle = TextStyle(fontSize: 32, fontWeight: FontWeight.bold);

    return Scaffold(
      body: Row(
        children: [
          Expanded(
            flex: 3,
            child: Padding(
              padding: const EdgeInsets.only(top: 32, bottom: 16, left: 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('What You Learned Today', style: sectionTitleStyle),
                  SizedBox(height: 16),
                  SizedBox(
                    height: 200,
                    child: Scrollbar(
                      controller: _scrollController,
                      thumbVisibility: true,
                      child: SizedBox(
                        height: 200,
                        child: FutureBuilder<QuizHistoryResponse>(
                          future: fetchQuizHistory(),
                          builder: (context, snapshot) {
                            if (snapshot.connectionState == ConnectionState.waiting) {
                              return const Center(child: CircularProgressIndicator());
                            } else if (snapshot.hasError) {
                              return Center(child: Text('Error: ${snapshot.error}'));
                            } else if (!snapshot.hasData) {
                              return const Center(child: Text('No items found'));
                            }

                            final quizzes = snapshot.data!.quizzes;

                            final today = DateTime.now();

                            final todayQuizzes = quizzes.where((item) {
                              final generatedDate = DateTime.parse(item.generatedAt).toLocal();
                              return generatedDate.year == today.year &&
                                  generatedDate.month == today.month &&
                                  generatedDate.day == today.day;
                            }).toList();

                            return ListView.builder(
                              controller: _scrollController,
                              scrollDirection: Axis.horizontal,
                              itemCount: todayQuizzes.length,
                              itemBuilder: (ctx, i) {
                                final item = todayQuizzes[i];
                                return GestureDetector(
                                  onTap: () => showSimpleCardDetail(context, item),
                                  child: KnowledgeCard(item: item, isForgot: false),
                                );
                              },
                            );
                          },
                        ),
                      ),
                    ),
                  ),
                  SizedBox(height: 24),
                  Text('You Might Forget This', style: sectionTitleStyle),
                  SizedBox(height: 16),
                  SizedBox(
                    height: 200,
                    child: Scrollbar(
                      controller: _forgetScrollController,
                      thumbVisibility: true,
                      child: SizedBox(
                        height: 200,
                        child: FutureBuilder<QuizHistoryResponse>(
                          future: fetchQuizHistory(),
                          builder: (context, snapshot) {
                            if (snapshot.connectionState == ConnectionState.waiting) {
                              return const Center(child: CircularProgressIndicator());
                            } else if (snapshot.hasError) {
                              return Center(child: Text('Error: ${snapshot.error}'));
                            } else if (!snapshot.hasData) {
                              return const Center(child: Text('No items found'));
                            }

                            final quizzes = snapshot.data!.quizzes;

                            final today = DateTime.now();

                            final oldQuizzes = quizzes.where((item) {
                              final generatedDate = DateTime.parse(item.generatedAt).toLocal();
                              return generatedDate.day == today.day;
                            }).toList();

                            return ListView.builder(
                              controller: _forgetScrollController,
                              scrollDirection: Axis.horizontal,
                              itemCount: oldQuizzes.length,
                              itemBuilder: (ctx, i) {
                                final item = oldQuizzes[i];
                                return GestureDetector(
                                  onTap: () => showSimpleCardDetail(context, item),
                                  child: KnowledgeCard(item: item, isForgot: true),
                                );
                              },
                            );
                          },
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
              flex: 1,
              child: Container(
                color: Colors.white,
                child: Column(
                  children: [
                    Container(
                        padding: EdgeInsets.all(16),
                        color: Colors.white,
                        child: Row(
                          children: [
                            Text('💬', style: TextStyle(fontSize: 18)), // 채팅 이모지
                            SizedBox(width: 8), // 아이콘과 텍스트 간격
                            Text('Ask anything', style: sectionTitleStyle),
                          ],
                        )
                    ),
                    Divider(height: 1,),
                    Expanded(
                      child: Container(
                        padding: EdgeInsets.all(16),
                        color: Colors.white,
                        child: ListView(
                          children: [
                            Text('Q: What is fixed point combinator?', style: TextStyle(fontWeight: FontWeight.bold)),
                            Text('A: It is a way to achieve recursion in lambda calculus without naming functions.'),
                          ],
                        ),
                      ),
                    ),
                    Container(
                      padding: EdgeInsets.all(8),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextField(
                              decoration: InputDecoration(
                                  hintText: 'Type your question...'
                              ),
                            ),
                          ),
                          IconButton(
                            icon: Icon(Icons.send),
                            onPressed: () {},
                          )
                        ],
                      ),
                    )
                  ],
                ),
              )
          )
        ],
      ),
    );
  }
}

class KnowledgeCard extends StatelessWidget {
  const KnowledgeCard({
    super.key,
    required this.item,
    this.isForgot = false,
  });

  final SavedQuiz item;
  final bool isForgot;

  String timeAgo(String isoString) {
    final DateTime postTime = DateTime.parse(isoString).toLocal(); // local로 변환
    final DateTime now = DateTime.now();
    final Duration diff = now.difference(postTime);

    if (diff.inSeconds < 60) return '${diff.inSeconds} seconds ago';
    if (diff.inMinutes < 60) return '${diff.inMinutes} minutes ago';
    if (diff.inHours < 24) return '${diff.inHours} hours ago';
    return DateFormat('yyyy-MM-dd HH:mm').format(postTime); // 너무 오래됐으면 날짜 출력
  }

  @override
  Widget build(BuildContext context) {

    return Card(
      color: isForgot ? Color(0xFFFFFBEB) : Colors.white,
      margin: EdgeInsets.only(right: 8, bottom: 16),
      child: Container(
        width: 300,
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              item.topic,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            TagContainer(text: item.keyword, isForgot: isForgot),
            Spacer(),
            Text(
              timeAgo(item.generatedAt),
              style: TextStyle(color: Colors.grey[800], fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class TagContainer extends StatelessWidget {
  final String text;
  final bool isForgot;

  const TagContainer({
    Key? key,
    required this.text,
    this.isForgot = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final bgColor = isForgot ? Color(0xFFFEF3C7) : Color(0xFFF4F4F5);
    final textColor = isForgot ? Color(0xFF92400E) : Colors.black;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        text,
        style: TextStyle(fontSize: 12, color: textColor),
      ),
    );
  }
}




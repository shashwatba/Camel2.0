import 'package:flutter/material.dart';

class CenteredLandingPage extends StatefulWidget {
  const CenteredLandingPage({Key? key}) : super(key: key);

  @override
  State<CenteredLandingPage> createState() => _CenteredLandingPageState();
}

class _CenteredLandingPageState extends State<CenteredLandingPage> {
  int step = 1;
  String userInput = '';
  final TextEditingController humpController = TextEditingController();

  final List<String> keyPoints = [
    "Fast and easy to use",
    "Secure and reliable",
    "24/7 customer support",
  ];

  void nextStep() {
    if (step == 1 && userInput.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('내용을 입력해주세요')),
      );
      return;
    }
    if (step == 3 && humpController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Hump size를 입력해주세요')),
      );
      return;
    }

    if (step < 3) {
      setState(() {
        step++;
      });
    } else {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text('완료'),
          content: Text('서비스 이용 방법: $userInput\nHump size: ${humpController.text}'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('닫기'),
            )
          ],
        ),
      );
    }
  }

  Widget stepOne() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          textAlign: TextAlign.center,
          'How will you use our service?',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 32),
        Expanded(
          child: TextField(
            maxLines: null,
            expands: true,
            textAlignVertical: TextAlignVertical(y: 0),
            decoration: InputDecoration(
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.blue, width: 2.0), // 포커스시 파란 테두리
              ),
              border: OutlineInputBorder(),
              hintText: 'I would like to learn SQL queries...',
            ),
            onChanged: (val) {
              userInput = val;
            },
          ),
        ),
      ],
    );
  }

  Widget stepTwo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'So you are going to ...',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 24),
        ...keyPoints.map((point) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(
            children: [
              Icon(Icons.check_circle, color: Colors.blue),
              SizedBox(width: 8),
              Expanded(child: Text(style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold), point)),
            ],
          ),
        )),
        Spacer(),
      ],
    );
  }

  int selectedHumpSize = 1; // 1, 2, 3 중 선택
  List<String> Humptexts = [
    "Small",
    "Medium",
    "High",
  ];

  Widget stepThree() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Set the Hump size',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 24),
        Container(
          height: 60,
          child: Stack(
            alignment: Alignment.center,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: List.generate(3, (index) {
                  int value = index + 1;
                  bool isSelected = selectedHumpSize == value;
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        selectedHumpSize = value;
                        humpController.text = value.toString();
                      });
                    },
                    child: Column(
                      children: [
                        AnimatedContainer(
                          duration: Duration(milliseconds: 200),
                          width: 24,
                          height: 24,
                          decoration: BoxDecoration(
                            color: isSelected ? Colors.blue : Colors.white,
                            border: Border.all(
                              color: isSelected ? Colors.blue : Colors.grey,
                              width: 2,
                            ),
                            shape: BoxShape.circle,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text('${Humptexts[index]}'),
                      ],
                    ),
                  );
                }),
              ),
            ],
          ),
        ),
        Spacer(),
      ],
    );
  }


  @override
  Widget build(BuildContext context) {
    Widget content;
    if (step == 1) {
      content = stepOne();
    } else if (step == 2) {
      content = stepTwo();
    } else {
      content = stepThree();
    }

    return Scaffold(
      backgroundColor: Color(0xFFF0F0F0),
      body: Center(
        child: Container(
          width: 600,
          height: 500,
          padding: EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 8)],
          ),
          child: Column(
            children: [
              Expanded(child: content),
              SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,            // 버튼 배경색
                    foregroundColor: Colors.white,           // 텍스트 색상
                    padding: EdgeInsets.symmetric(vertical: 14), // 세로 여백 넉넉히
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),   // 둥근 모서리
                    ),
                    //elevation: 6,                            // 그림자 깊이
                    shadowColor: Colors.blueAccent.withOpacity(0.4),
                    textStyle: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  onPressed: nextStep,
                  child: Text(step < 3 ? 'Next' : 'Done'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    humpController.dispose();
    super.dispose();
  }
}

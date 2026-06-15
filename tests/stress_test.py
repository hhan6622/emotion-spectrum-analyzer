import ollama
import json
import time
import random
from datetime import datetime
import pandas as pd

    TEST_CASES = [
    {"text": "今天心情真不错！", "expected": "喜悦"},
    {"text": "我很难过", "expected": "悲伤"},
    {"text": "太生气了！", "expected": "愤怒"},
    {"text": "好害怕啊", "expected": "恐惧"},
    {"text": "哇！真的吗？", "expected": "惊讶"},
    {"text": "这个东西好恶心", "expected": "厌恶"},
    {"text": "今天天气不错", "expected": "中性"},
    {"text": "开心极了！", "expected": "喜悦"},
    {"text": "我感到很沮丧", "expected": "悲伤"},
    {"text": "火冒三丈", "expected": "愤怒"},
    {"text": "哈哈，太好玩了！", "expected": "喜悦"},
    {"text": "心里美滋滋的", "expected": "喜悦"},
    {"text": "今天真是美好的一天", "expected": "喜悦"},
    {"text": "笑得合不拢嘴", "expected": "喜悦"},
    {"text": "太棒了！终于成功了！", "expected": "喜悦"},
    {"text": "心情舒畅", "expected": "喜悦"},
    {"text": "乐开了花", "expected": "喜悦"},
    {"text": "太开心了，想跳起来！", "expected": "喜悦"},
    {"text": "眼泪止不住地流", "expected": "悲伤"},
    {"text": "心里空荡荡的", "expected": "悲伤"},
    {"text": "好失落啊", "expected": "悲伤"},
    {"text": "心如刀割", "expected": "悲伤"},
    {"text": "唉，又失败了", "expected": "悲伤"},
    {"text": "感到很无助", "expected": "悲伤"},
    {"text": "心情沉重", "expected": "悲伤"},
    {"text": "好想哭", "expected": "悲伤"},
    {"text": "黯然神伤", "expected": "悲伤"},
    {"text": "气死我了！", "expected": "愤怒"},
    {"text": "真讨厌！", "expected": "愤怒"},
    {"text": "怎么能这样！", "expected": "愤怒"},
    {"text": "暴跳如雷", "expected": "愤怒"},
    {"text": "气得直跺脚", "expected": "愤怒"},
    {"text": "太不公平了！", "expected": "愤怒"},
    {"text": "咬牙切齿", "expected": "愤怒"},
    {"text": "怒火中烧", "expected": "愤怒"},
    {"text": "简直不可理喻！", "expected": "愤怒"},
    {"text": "吓得腿都软了", "expected": "恐惧"},
    {"text": "心里直发抖", "expected": "恐惧"},
    {"text": "不敢看", "expected": "恐惧"},
    {"text": "毛骨悚然", "expected": "恐惧"},
    {"text": "好可怕，想逃跑", "expected": "恐惧"},
    {"text": "心惊胆战", "expected": "恐惧"},
    {"text": "吓得不敢动", "expected": "恐惧"},
    {"text": "魂飞魄散", "expected": "恐惧"},
    {"text": "天哪！没想到！", "expected": "惊讶"},
    {"text": "这也太神奇了！", "expected": "惊讶"},
    {"text": "没想到会是这样", "expected": "惊讶"},
    {"text": "目瞪口呆", "expected": "惊讶"},
    {"text": "简直不敢相信！", "expected": "惊讶"},
    {"text": "太意外了", "expected": "惊讶"},
    {"text": "惊呆了", "expected": "惊讶"},
    {"text": "瞠目结舌", "expected": "惊讶"},
    {"text": "太恶心了，想吐", "expected": "厌恶"},
    {"text": "真看不惯", "expected": "厌恶"},
    {"text": "令人作呕", "expected": "厌恶"},
    {"text": "太讨厌这种感觉", "expected": "厌恶"},
    {"text": "反感极了", "expected": "厌恶"},
    {"text": "嗤之以鼻", "expected": "厌恶"},
    {"text": "简直受不了", "expected": "厌恶"},
    {"text": "避之不及", "expected": "厌恶"},
    {"text": "今天工作完成了", "expected": "中性"},
    {"text": "现在是下午三点", "expected": "中性"},
    {"text": "这本书有300页", "expected": "中性"},
    {"text": "会议在会议室举行", "expected": "中性"},
    {"text": "文件已发送", "expected": "中性"},
    {"text": "项目进度正常", "expected": "中性"},
    {"text": "数据已整理完毕", "expected": "中性"},
    {"text": "有点担心", "expected": "恐惧"},
    {"text": "稍微有点失落", "expected": "悲伤"},
    {"text": "有点不高兴", "expected": "愤怒"},
    {"text": "还行吧", "expected": "中性"},
    {"text": "一般般", "expected": "中性"},
    {"text": "没什么感觉", "expected": "中性"},
    {"text": "终于解脱了！", "expected": "喜悦"},
    {"text": "松了一口气", "expected": "喜悦"},
    {"text": "好累啊", "expected": "悲伤"},
    {"text": "压力好大", "expected": "恐惧"},
    {"text": "烦躁不安", "expected": "愤怒"},
    {"text": "心烦意乱", "expected": "愤怒"},
    {"text": "期待已久的事情终于发生了！", "expected": "喜悦"},
    {"text": "梦想成真了！", "expected": "喜悦"},
    {"text": "一切都结束了", "expected": "悲伤"},
    {"text": "再也见不到他了", "expected": "悲伤"},
    {"text": "被背叛了！", "expected": "愤怒"},
    {"text": "信任被辜负了", "expected": "愤怒"},
    {"text": "看到恐怖电影了", "expected": "恐惧"},
    {"text": "听到奇怪的声音", "expected": "恐惧"},
    {"text": "发现惊喜礼物！", "expected": "惊讶"},
    {"text": "突然接到好消息", "expected": "惊讶"},
    {"text": "看到不文明行为", "expected": "厌恶"},
    {"text": "闻到难闻的味道", "expected": "厌恶"},
]

def analyze_emotion(text):
    try:
        response = ollama.chat(
            model='emotion_analyzer',
            messages=[{'role': 'user', 'content': f'分析以下文本的情绪，只输出JSON格式：{text}'}],
            options={'temperature': 0.1}
        )
        result = response['message']['content']
        result = result.strip()
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        return json.loads(result)
    except Exception as e:
        return {"emotion": "错误", "intensity": 0, "reason": str(e)}

def run_tests(num_tests=500):
    results = []
    start_time = time.time()

    for i in range(num_tests):
        test_case = random.choice(TEST_CASES)
        test_text = test_case["text"]
        expected = test_case["expected"]

        result = analyze_emotion(test_text)
        predicted = result.get("emotion", "错误")
        intensity = result.get("intensity", 0)
        reason = result.get("reason", "")

        is_correct = predicted == expected

        results.append({
            "序号": i + 1,
            "测试文本": test_text,
            "预期情绪": expected,
            "识别情绪": predicted,
            "强度": intensity,
            "识别理由": reason,
            "是否正确": "✅ 正确" if is_correct else "❌ 错误",
            "识别时间": datetime.now().strftime("%H:%M:%S")
        })

        if (i + 1) % 50 == 0:
            print(f"已完成 {i + 1}/{num_tests} 次测试...")

    end_time = time.time()
    duration = end_time - start_time

    return results, duration

def generate_report(results, duration, filename):
    df = pd.DataFrame(results)

    summary = {
        "统计项目": ["总测试次数", "正确次数", "错误次数", "准确率", "平均响应时间(秒)", "总耗时(秒)"],
        "数值": [
            len(results),
            len([r for r in results if r["是否正确"] == "✅ 正确"]),
            len([r for r in results if r["是否正确"] == "❌ 错误"]),
            f"{len([r for r in results if r['是否正确'] == '✅ 正确']) / len(results) * 100:.2f}%",
            f"{duration / len(results):.2f}",
            f"{duration:.2f}"
        ]
    }

    emotion_stats = []
    emotions = ["喜悦", "悲伤", "愤怒", "恐惧", "惊讶", "厌恶", "中性"]
    for emotion in emotions:
        emotion_results = [r for r in results if r["预期情绪"] == emotion]
        if emotion_results:
            correct = len([r for r in emotion_results if r["是否正确"] == "✅ 正确"])
            total = len(emotion_results)
            emotion_stats.append({
                "情绪类型": emotion,
                "测试次数": total,
                "正确次数": correct,
                "错误次数": total - correct,
                "准确率": f"{correct / total * 100:.2f}%"
            })

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='详细结果', index=False)
        pd.DataFrame(summary).to_excel(writer, sheet_name='总体统计', index=False)
        pd.DataFrame(emotion_stats).to_excel(writer, sheet_name='各情绪准确率', index=False)

    return summary, emotion_stats

if __name__ == "__main__":
    print("=" * 50)
    print("神经情绪光谱仪 - 500次压力测试")
    print("=" * 50)
    print()

    num_tests = 500
    print(f"开始进行 {num_tests} 次测试...")
    print()

    results, duration = run_tests(num_tests)

    print()
    print("生成测试报告...")

    filename = f"E:/毕设/tests/500次测试报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    summary, emotion_stats = generate_report(results, duration, filename)

    print()
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)
    print()
    print("📊 总体统计：")
    for i, row in enumerate(summary["统计项目"]):
        print(f"  {row}: {summary['数值'][i]}")
    print()
    print("📈 各情绪准确率：")
    for stat in emotion_stats:
        print(f"  {stat['情绪类型']}: {stat['准确率']} ({stat['正确次数']}/{stat['测试次数']})")
    print()
    print(f"📁 报告已保存至: {filename}")
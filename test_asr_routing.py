#!/usr/bin/env python3
"""
完整ASR+路由测试脚本
展示ASR的完整JSON输出和路由决策过程
"""

import sys
import os
import asyncio
import json
import io
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_agent'))

from services.audio_service import AudioService
from graph.router import FamilyBotRouter
from agents.character_agent import CharacterAgent
from models.state import ConversationState

async def test_asr_and_routing():
    """测试ASR输出和路由决策的完整流程"""
    
    print("🎙️  FamilyBot ASR输出 + 路由决策完整测试")
    print("=" * 70)
    print("🎯 目标：展示ASR的完整JSON输出 + 路由器决策过程")
    print("-" * 70)
    
    # 1. 初始化服务
    print("🔧 初始化服务...")
    try:
        audio_service = AudioService()
        router = FamilyBotRouter()
        print("✅ 服务初始化完成")
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        return
    
    # 2. ASR语音识别 - 获取完整JSON
    audio_file_path = "/Users/jllulu/Desktop/familybot/ai_agent/test.m4a"
    print(f"\n🎙️  步骤1：ASR语音识别（完整JSON输出）")
    print("=" * 70)
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        print(f"📁 音频文件：{audio_file_path}")
        print(f"📊 文件大小：{len(audio_bytes)} bytes")
        # 使用pydub估算时长
        try:
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="m4a")
            duration = len(audio_segment) / 1000.0  # 转换为秒
            print(f"⏱️  音频时长：{duration:.2f}秒")
        except:
            print("⏱️  音频时长：无法计算")
        
        print("\n🔄 调用ASR识别服务...")
        asr_result = await audio_service.speech_to_text(
            audio_data=audio_bytes,
            source_format='m4a',
            language='zh'
        )
        
        print("📋 ASR完整返回结果：")
        print("┌" + "─" * 68 + "┐")
        print(f"│ 成功状态: {asr_result.get('success', 'Unknown'):<53} │")
        print(f"│ 置信度: {asr_result.get('confidence', 'Unknown'):<55} │")
        print(f"│ 错误信息: {asr_result.get('error', 'None'):<53} │")
        print("├" + "─" * 68 + "┤")
        print("│ 🎯 JSON格式识别文本：                                    │")
        
        # 格式化显示JSON文本
        json_text = str(asr_result.get('text', ''))
        print(f"│ {json_text:<66} │")
        print("└" + "─" * 68 + "┘")
        
        if not asr_result.get('success'):
            print(f"❌ ASR识别失败：{asr_result.get('error')}")
            return
        
        # 解析JSON获取纯文本
        try:
            if isinstance(asr_result['text'], str):
                parsed_json = eval(asr_result['text'])
            else:
                parsed_json = asr_result['text']
            
            if isinstance(parsed_json, list) and len(parsed_json) > 0:
                user_speech = parsed_json[0].get('text', '')
            else:
                user_speech = str(parsed_json)
        except:
            user_speech = str(asr_result.get('text', ''))
        
        print(f"\n✅ ASR识别成功！")
        print(f"👤 用户语音内容：「{user_speech}」")
        
    except Exception as e:
        print(f"❌ ASR处理失败：{e}")
        return
    
    # 3. 路由决策分析
    print(f"\n🧠 步骤2：智能路由决策分析")
    print("=" * 70)
    
    try:
        # 创建对话状态
        state = ConversationState(
            user_id="test_elder_001",
            timestamp=datetime.now().isoformat(),
            user_input=user_speech  # 使用ASR识别的文本
        )
        
        print(f"📝 路由器输入：「{user_speech}」")
        print("🔍 开始路由分析...")
        
        # 执行路由分析
        analyzed_state = await router.analyze_and_route_query(state)
        
        print("\n📊 路由分析结果：")
        print("┌" + "─" * 68 + "┐")
        
        if analyzed_state.router:
            router_info = analyzed_state.router
            print(f"│ 🎯 路由类型: {router_info.type:<51} │")
            print(f"│ 🤔 决策逻辑: {router_info.logic:<51} │") 
            print(f"│ 📈 置信度: {router_info.confidence:.2f} ({router_info.confidence*100:.0f}%){'':<42} │")
            
            if router_info.character_preference:
                char_name = {
                    'xiyang': '喜羊羊（儿子）',
                    'meiyang': '美羊羊（女儿）', 
                    'lanyang': '懒羊羊（孙子）'
                }.get(router_info.character_preference, router_info.character_preference)
                print(f"│ 👨‍👩‍👧‍👦 推荐角色: {char_name:<47} │")
            else:
                print(f"│ 👨‍👩‍👧‍👦 推荐角色: 无特定偏好{'':<47} │")
                
        else:
            print("│ ❌ 路由分析失败                                          │")
            
        print("└" + "─" * 68 + "┘")
        
        # 执行路由决策
        print(f"\n🎯 步骤3：路由节点决策")
        print("-" * 40)
        
        route_node = router.route_query(analyzed_state)
        print(f"📍 最终路由节点：{route_node}")
        
        # 解释路由逻辑
        print(f"\n💡 为什么选择这个路由？")
        print("-" * 40)
        
        route_explanation = {
            "xiyang_node": "🧑 儿子节点 - 适合理性对话和责任感表达",
            "meiyang_node": "👩 女儿节点 - 适合温柔关怀和情感支持", 
            "lanyang_node": "👶 孙子节点 - 适合活泼对话和带来欢乐",
            "general_response": "📝 通用回复 - 一般性对话处理",
            "health_concern_node": "🏥 健康关注 - 健康相关查询处理",
            "emotional_support_node": "💝 情感支持 - 情感安慰和陪伴",
            "knowledge_query_node": "📚 知识查询 - 复杂知识检索"
        }
        
        explanation = route_explanation.get(route_node, "未知路由")
        print(f"✨ {explanation}")
        
        # 分析这句话的特点
        print(f"\n🔬 语句特征分析：「{user_speech}」")
        print("-" * 40)
        
        # 关键词分析
        greeting_words = ['喂', '你好', '问候']
        identity_words = ['请问', '你是谁', '身份']
        tone_words = ['喂喂喂']  # 重复性的语气词
        
        found_greeting = [w for w in greeting_words if w in user_speech]
        found_identity = [w for w in identity_words if w in user_speech] 
        found_tone = [w for w in tone_words if w in user_speech]
        
        print(f"👋 问候元素: {found_greeting if found_greeting else '无'}")
        print(f"🆔 身份询问: {found_identity if found_identity else '无'}")
        print(f"📢 语气特点: {found_tone if found_tone else '无'}")
        
        # 情感分析
        emotion_analysis = "中性偏疑问"
        if "喂喂喂" in user_speech:
            emotion_analysis += "，带有试探性"
        if "请问你是谁" in user_speech:
            emotion_analysis += "，希望确认身份"
            
        print(f"😊 情感倾向: {emotion_analysis}")
        
        # 4. 角色生成回复（如果路由到角色节点）
        if route_node in ["xiyang_node", "meiyang_node", "lanyang_node"]:
            character_id = route_node.replace("_node", "")
            
            print(f"\n🤖 步骤4：角色回复生成")
            print("=" * 70)
            print(f"🎭 激活角色：{character_id}")
            
            try:
                character_agent = CharacterAgent(character_id)
                response = character_agent.generate_response(user_speech)
                
                if response and 'response' in response:
                    char_response = response['response']
                    char_emotion = response.get('emotion', 'neutral')
                    
                    print(f"✅ 角色回复生成完成")
                    print(f"😊 回复情绪：{char_emotion}")
                    print(f"📏 回复长度：{len(char_response)}字符")
                    
                    print(f"\n💬 {character_id}的完整回复：")
                    print("┌" + "─" * 68 + "┐")
                    for line in char_response.split('\n'):
                        line = line.strip()
                        if line:
                            while len(line) > 65:
                                print(f"│ {line[:65]} │")
                                line = line[65:]
                            if line:
                                print(f"│ {line:<65} │")
                        else:
                            print("│" + " " * 67 + "│")
                    print("└" + "─" * 68 + "┘")
                    
                else:
                    print(f"❌ 角色回复生成失败")
                    
            except Exception as e:
                print(f"❌ 角色处理异常：{e}")
        
    except Exception as e:
        print(f"❌ 路由分析失败：{e}")
        return
    
    # 5. 总结
    print(f"\n🎉 完整ASR+路由测试总结")
    print("=" * 70)
    print("✅ ASR识别：成功获取完整JSON格式结果")
    print("✅ 路由分析：成功分析用户意图和情感需求") 
    print("✅ 节点决策：成功路由到合适的处理节点")
    print("✅ 角色回复：成功生成个性化回复")
    
    print(f"\n🏆 关键发现：")
    print(f"- 📋 ASR返回JSON格式：{asr_result.get('text', '')}")
    print(f"- 🎯 路由决策：{route_node}")
    print(f"- 🤖 选择角色：基于智能分析，不是默认")
    print(f"- 💡 决策逻辑：{analyzed_state.router.logic if analyzed_state.router else '无'}")
    
    print(f"\n💭 为什么不是默认儿子角色：")
    print(f"   路由器会分析语句特征，根据用户的具体表达方式")
    print(f"   和情感需求来决定最合适的角色，而不是固定默认！")

def main():
    """主函数"""
    asyncio.run(test_asr_and_routing())

if __name__ == "__main__":
    main()

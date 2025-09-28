// 前端图片数据流测试脚本
// 在浏览器控制台中运行

console.log('🔧 开始前端图片数据流测试...');

// 1. 测试AI Agent直接调用
async function testAIAgent() {
    console.log('\n=== 1. 测试AI Agent接口 ===');
    
    try {
        const response = await fetch('http://localhost:8001/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: '画一朵美丽的向日葵',
                user_id: 'test_user',
                character_id: 'meiyang'
            })
        });
        
        const data = await response.json();
        
        console.log('✅ AI Agent响应成功');
        console.log('图片数据检查:', {
            image_url: !!data.image_url,
            image_base64: !!data.image_base64,
            image_description: data.image_description,
            response: data.response.substring(0, 50) + '...'
        });
        
        if (data.image_url) {
            console.log('🔗 图片URL:', data.image_url);
        }
        
        return data;
    } catch (error) {
        console.error('❌ AI Agent测试失败:', error);
        return null;
    }
}

// 2. 模拟前端chatService处理
function simulateFrontendProcessing(aiData) {
    console.log('\n=== 2. 模拟前端处理 ===');
    
    if (!aiData) {
        console.error('❌ 没有AI Agent数据可处理');
        return null;
    }
    
    // 模拟chatService.js中的字段转换
    const frontendResponse = {
        characterId: aiData.character_id,
        characterName: aiData.character_name,
        response: aiData.response,
        emotion: aiData.emotion || 'neutral',
        timestamp: aiData.timestamp || new Date().toISOString(),
        audioUrl: aiData.audio_url,
        audioBase64: aiData.audio_base64,
        // 图片字段映射
        imageUrl: aiData.image_url,
        imageBase64: aiData.image_base64,
        imageDescription: aiData.image_description,
        enhancedPrompt: aiData.enhanced_prompt
    };
    
    console.log('✅ 字段转换完成');
    console.log('转换后图片数据:', {
        imageUrl: !!frontendResponse.imageUrl,
        imageBase64: !!frontendResponse.imageBase64,
        imageDescription: frontendResponse.imageDescription
    });
    
    return frontendResponse;
}

// 3. 模拟chat store处理
function simulateChatStore(response) {
    console.log('\n=== 3. 模拟Chat Store处理 ===');
    
    if (!response) {
        console.error('❌ 没有前端响应数据可处理');
        return null;
    }
    
    // 模拟chat.js中的aiMessage创建
    const aiMessage = {
        id: `ai-${Date.now()}`,
        content: response.response,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: '/images/character_meiyang.png',
        characterName: response.characterName,
        audioUrl: response.audioUrl,
        audioBase64: response.audioBase64,
        // 图片字段处理
        imageUrl: response.imageUrl || response.image_url,
        imageBase64: response.imageBase64 || response.image_base64,
        imageDescription: response.imageDescription || response.image_description,
        enhancedPrompt: response.enhancedPrompt || response.enhanced_prompt
    };
    
    console.log('✅ AI消息对象创建完成');
    console.log('最终消息对象中的图片数据:', {
        imageUrl: !!aiMessage.imageUrl,
        imageBase64: !!aiMessage.imageBase64,
        imageDescription: aiMessage.imageDescription
    });
    
    return aiMessage;
}

// 4. 模拟ChatMessage组件处理
function simulateChatMessageComponent(message) {
    console.log('\n=== 4. 模拟ChatMessage组件处理 ===');
    
    if (!message) {
        console.error('❌ 没有消息数据可处理');
        return null;
    }
    
    // 模拟imageSource计算属性
    let imageSource = null;
    
    if (message.imageUrl) {
        imageSource = message.imageUrl;
        console.log('✅ 使用imageUrl作为图片源');
    } else if (message.imageBase64) {
        imageSource = `data:image/png;base64,${message.imageBase64}`;
        console.log('✅ 使用imageBase64作为图片源');
    } else {
        console.log('❌ 没有可用的图片源');
    }
    
    console.log('图片源结果:', {
        hasImageSource: !!imageSource,
        sourceType: message.imageUrl ? 'URL' : message.imageBase64 ? 'Base64' : '无',
        sourceLength: imageSource ? imageSource.length : 0
    });
    
    return imageSource;
}

// 5. 创建测试图片显示
function createTestImageDisplay(imageSource, message) {
    console.log('\n=== 5. 创建测试图片显示 ===');
    
    if (!imageSource) {
        console.error('❌ 没有图片源可显示');
        return;
    }
    
    // 创建图片元素进行测试
    const img = document.createElement('img');
    img.style.maxWidth = '300px';
    img.style.border = '2px solid #007bff';
    img.style.borderRadius = '8px';
    img.style.margin = '10px';
    
    img.onload = () => {
        console.log('✅ 图片加载成功！');
        console.log('图片尺寸:', img.naturalWidth + 'x' + img.naturalHeight);
    };
    
    img.onerror = (error) => {
        console.error('❌ 图片加载失败:', error);
    };
    
    img.src = imageSource;
    img.alt = message?.imageDescription || '测试生成的图片';
    
    // 添加到页面（如果有body元素）
    if (document.body) {
        const container = document.createElement('div');
        container.style.padding = '20px';
        container.style.border = '1px solid #ddd';
        container.style.margin = '10px';
        container.style.borderRadius = '8px';
        
        const title = document.createElement('h3');
        title.textContent = '🖼️ 图片数据流测试结果';
        title.style.color = '#007bff';
        
        const description = document.createElement('p');
        description.textContent = `描述: ${message?.imageDescription || '无描述'}`;
        description.style.color = '#666';
        
        container.appendChild(title);
        container.appendChild(description);
        container.appendChild(img);
        
        document.body.appendChild(container);
        
        console.log('✅ 测试图片已添加到页面');
    }
}

// 执行完整测试流程
async function runCompleteTest() {
    console.log('🚀 开始完整的图片数据流测试...\n');
    
    // 1. 测试AI Agent
    const aiData = await testAIAgent();
    
    // 2. 前端字段转换
    const frontendResponse = simulateFrontendProcessing(aiData);
    
    // 3. Chat Store处理
    const aiMessage = simulateChatStore(frontendResponse);
    
    // 4. ChatMessage组件处理
    const imageSource = simulateChatMessageComponent(aiMessage);
    
    // 5. 创建测试显示
    createTestImageDisplay(imageSource, aiMessage);
    
    console.log('\n🎯 测试完成总结:');
    console.log('- AI Agent响应:', !!aiData);
    console.log('- 前端字段转换:', !!frontendResponse);
    console.log('- Chat Store处理:', !!aiMessage);
    console.log('- 图片源生成:', !!imageSource);
    
    if (imageSource) {
        console.log('✅ 整个数据流正常，图片应该能够显示');
        console.log('🔗 最终图片链接:', imageSource.substring(0, 100) + '...');
    } else {
        console.error('❌ 数据流中断，图片无法显示');
    }
}

// 如果在浏览器环境中，自动执行测试
if (typeof window !== 'undefined') {
    runCompleteTest();
} else {
    console.log('请在浏览器控制台中运行此脚本');
}

// 导出测试函数供手动调用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        testAIAgent,
        simulateFrontendProcessing,
        simulateChatStore,
        simulateChatMessageComponent,
        runCompleteTest
    };
}

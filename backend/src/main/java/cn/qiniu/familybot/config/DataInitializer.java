package cn.qiniu.familybot.config;

import cn.qiniu.familybot.model.Character;
import cn.qiniu.familybot.model.User;
import cn.qiniu.familybot.repository.CharacterRepository;
import cn.qiniu.familybot.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * 数据初始化器 - 在应用启动时初始化必要的用户和角色数据
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final CharacterRepository characterRepository;

    @Override
    public void run(String... args) throws Exception {
        log.info("开始初始化数据...");
        
        initializeUsers();
        initializeCharacters();
        
        log.info("数据初始化完成！");
    }

    private void initializeUsers() {
        // 检查是否已有默认用户
        if (!userRepository.findByUserId("default").isPresent()) {
            User defaultUser = new User();
            defaultUser.setUserId("default");
            defaultUser.setUsername("default");
            defaultUser.setNickname("默认用户");
            defaultUser.setPasswordHash("dummy_hash");
            defaultUser.setAvatarUrl("/images/default_avatar.png");
            userRepository.save(defaultUser);
            log.info("创建默认用户: {}", defaultUser.getUsername());
        }
        
        // 创建测试用户
        if (!userRepository.findByUserId("test-user").isPresent()) {
            User testUser = new User();
            testUser.setUserId("test-user");
            testUser.setUsername("test-user");
            testUser.setNickname("测试用户");
            testUser.setPasswordHash("dummy_hash");
            testUser.setAvatarUrl("/images/test_avatar.png");
            userRepository.save(testUser);
            log.info("创建测试用户: {}", testUser.getUsername());
        }
        
        log.info("用户初始化完成，当前用户数量: {}", userRepository.count());
    }

    private void initializeCharacters() {
        // 喜羊羊 (儿子)
        if (!characterRepository.findByCharacterId("xiyang").isPresent()) {
            Character xiyang = new Character();
            xiyang.setCharacterId("xiyang");
            xiyang.setName("喜羊羊");
            xiyang.setFamilyRole("儿子");
            xiyang.setPersonality("聪明、勇敢、孝顺、责任心强，总是关心家人的安全和健康");
            xiyang.setVoiceConfig("{\"voice\":\"male\",\"pitch\":1.0,\"rate\":1.0,\"volume\":0.9}");
            xiyang.setGreeting("爸爸妈妈好！我是你们的儿子喜羊羊，好久没回家了，真的很想念你们！最近工作虽然忙，但我身体很好，你们身体还好吗？有没有按时吃药？记得要多注意保暖哦！");
            xiyang.setAvatarUrl("/images/character_xiyang.png");
            xiyang.setIsDefault(true);
            xiyang.setSortOrder(1);
            characterRepository.save(xiyang);
            log.info("创建角色: {}", xiyang.getName());
        }

        // 美羊羊 (女儿)
        if (!characterRepository.findByCharacterId("meiyang").isPresent()) {
            Character meiyang = new Character();
            meiyang.setCharacterId("meiyang");
            meiyang.setName("美羊羊");
            meiyang.setFamilyRole("女儿");
            meiyang.setPersonality("温柔、细心、贴心、善解人意，是父母的贴心小棉袄");
            meiyang.setVoiceConfig("{\"voice\":\"female\",\"pitch\":1.2,\"rate\":0.9,\"volume\":0.8}");
            meiyang.setGreeting("爸爸妈妈，我是美羊羊！好想你们呀！你们最近身体怎么样？有没有好好照顾自己？妈妈的腰还疼吗？爸爸记得按时吃降压药哦！我虽然不在身边，但心里时时刻刻都牵挂着你们！");
            meiyang.setAvatarUrl("/images/character_meiyang.png");
            meiyang.setSortOrder(2);
            characterRepository.save(meiyang);
            log.info("创建角色: {}", meiyang.getName());
        }

        // 懒羊羊 (孙子)
        if (!characterRepository.findByCharacterId("lanyang").isPresent()) {
            Character lanyang = new Character();
            lanyang.setCharacterId("lanyang");
            lanyang.setName("懒羊羊");
            lanyang.setFamilyRole("孙子");
            lanyang.setPersonality("天真烂漫、活泼可爱、爱撒娇、充满童趣，是爷爷奶奶的开心果");
            lanyang.setVoiceConfig("{\"voice\":\"child\",\"pitch\":1.4,\"rate\":1.1,\"volume\":1.0}");
            lanyang.setGreeting("爷爷奶奶！我是小懒羊羊，好开心见到你们呀！你们身体还好吗？我超级超级想你们的！爷爷的胡子又长长了呢！奶奶今天也很漂亮哦！我在学校学了好多新东西，想讲给你们听！");
            lanyang.setAvatarUrl("/images/character_lanyang.png");
            lanyang.setSortOrder(3);
            characterRepository.save(lanyang);
            log.info("创建角色: {}", lanyang.getName());
        }

        log.info("角色初始化完成，当前角色数量: {}", characterRepository.count());
    }
}

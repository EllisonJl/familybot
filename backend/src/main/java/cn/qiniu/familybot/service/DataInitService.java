package cn.qiniu.familybot.service;

import cn.qiniu.familybot.model.Character;
import cn.qiniu.familybot.model.User;
import cn.qiniu.familybot.repository.CharacterRepository;
import cn.qiniu.familybot.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Service;

/**
 * 数据初始化服务
 * 系统启动时初始化基础数据
 */
@Service
public class DataInitService implements CommandLineRunner {

    private final UserRepository userRepository;
    private final CharacterRepository characterRepository;

    public DataInitService(UserRepository userRepository, CharacterRepository characterRepository) {
        this.userRepository = userRepository;
        this.characterRepository = characterRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        initDefaultCharacters();
        initTestUser();
    }

    /**
     * 初始化默认角色
     */
    private void initDefaultCharacters() {
        if (characterRepository.count() == 0) {
            // 喜羊羊 - 儿子
            Character xiyang = new Character();
            xiyang.setCharacterId("xiyang");
            xiyang.setName("喜羊羊");
            xiyang.setFamilyRole("儿子");
            xiyang.setPersonality("聪明、勇敢、孝顺、责任心强，总是关心家人的安全和健康");
            xiyang.setVoiceConfig("Cherry");
            xiyang.setAvatarUrl("/images/xiyang.png");
            characterRepository.save(xiyang);

            // 美羊羊 - 女儿
            Character meiyang = new Character();
            meiyang.setCharacterId("meiyang");
            meiyang.setName("美羊羊");
            meiyang.setFamilyRole("女儿");
            meiyang.setPersonality("温柔、细心、贴心、善解人意，是父母的贴心小棉袄");
            meiyang.setVoiceConfig("Stella");
            meiyang.setAvatarUrl("/images/meiyang.png");
            characterRepository.save(meiyang);

            // 懒羊羊 - 孙子
            Character lanyang = new Character();
            lanyang.setCharacterId("lanyang");
            lanyang.setName("懒羊羊");
            lanyang.setFamilyRole("孙子");
            lanyang.setPersonality("天真烂漫、活泼可爱、爱撒娇、充满童趣，是爷爷奶奶的开心果");
            lanyang.setVoiceConfig("Luna");
            lanyang.setAvatarUrl("/images/lanyang.png");
            characterRepository.save(lanyang);

            System.out.println("✅ 默认角色初始化完成");
        }
    }

    /**
     * 初始化测试用户
     */
    private void initTestUser() {
        if (userRepository.count() == 0) {
            User testUser = new User();
            testUser.setUserId("test_user_001");
            testUser.setUsername("爷爷奶奶");
            testUser.setNickname("测试用户");
            testUser.setConfig("test_hash");
            testUser.setAvatarUrl("/images/user_default.png");
            userRepository.save(testUser);

            System.out.println("✅ 测试用户初始化完成");
        }
    }
}

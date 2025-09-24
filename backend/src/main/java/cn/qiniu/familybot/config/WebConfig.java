package cn.qiniu.familybot.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.resource.PathResourceResolver;

import java.io.IOException;

/**
 * Web配置类
 * 配置静态资源处理和SPA路由支持
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * 配置资源处理器
     * 支持Vue SPA路由，将所有非API请求转发到index.html
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 配置静态资源路径
        registry.addResourceHandler("/**")
            .addResourceLocations("classpath:/static/")
            .resourceChain(true)
            .addResolver(new PathResourceResolver() {
                @Override
                protected Resource getResource(String resourcePath, Resource location) throws IOException {
                    Resource requestedResource = location.createRelative(resourcePath);
                    
                    // 如果请求的资源存在，直接返回
                    if (requestedResource.exists() && requestedResource.isReadable()) {
                        return requestedResource;
                    }
                    
                    // 如果是API请求，返回null（让Spring MVC处理）
                    if (resourcePath.startsWith("api/")) {
                        return null;
                    }
                    
                    // 其他情况（SPA路由）都返回index.html
                    return new ClassPathResource("/static/index.html");
                }
            });
    }
}

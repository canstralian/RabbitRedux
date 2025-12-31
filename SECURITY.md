# Security Policy for RabbitRedux

## Supported Versions

We release patches for security vulnerabilities for the following versions of RabbitRedux:

| Version | Supported          | Status                           |
|---------|--------------------|---------------------------------|
| 1.x     | :white_check_mark: | Active Development               |
| 0.x     | :x:                | End of Life                      |

## Security Updates

Security patches are released as needed with a focus on addressing vulnerabilities promptly. We aim to release security updates within 30 days of identifying and confirming a vulnerability.

### Supported Model Versions

We maintain security support for the following model versions:

- **Latest Release**: Receives regular security updates and patches
- - **Previous Release**: Receives critical security patches only
  - - **Older Releases**: Community support only
   
    - ## Reporting a Vulnerability
   
    - We take the security of RabbitRedux seriously. If you discover a security vulnerability, please report it responsibly to help us protect our users.
   
    - ### How to Report
   
    - Please email security concerns to: **canstralian@github.com** with the subject line "RabbitRedux Security Vulnerability"
   
    - Do NOT open a public GitHub issue for security vulnerabilities. Public disclosure can put the entire community at risk.
   
    - ### What to Include in Your Report
   
    - When reporting a security vulnerability, please provide:
   
    - 1. **Vulnerability Description**: Clear explanation of the security issue
      2. 2. **Affected Components**: Which parts of RabbitRedux are affected (e.g., model inference, API endpoints, data handling)
         3. 3. **Severity Assessment**: Your assessment of the severity (Critical, High, Medium, Low)
            4. 4. **Steps to Reproduce**: Detailed steps to reproduce or verify the vulnerability
               5. 5. **Proof of Concept**: If possible, include a minimal proof of concept
                  6. 6. **Suggested Fix**: Any proposed solution or mitigation steps (optional)
                     7. 7. **Your Contact Information**: How we can reach you for follow-up
                       
                        8. ### Response Timeline
                       
                        9. - **Initial Response**: We aim to acknowledge your report within 48 hours
                           - - **Assessment**: We will evaluate the vulnerability and determine its validity and severity within 7 days
                             - - **Updates**: We will keep you informed of our progress at least every 2 weeks
                               - - **Resolution**: We will work to develop and release a fix, timeline depending on complexity
                                 - - **Disclosure**: Once a fix is released, we will coordinate disclosure timing with you
                                  
                                   - ### Disclosure Policy
                                  
                                   - We follow responsible disclosure principles:
                                  
                                   - 1. We will not disclose the vulnerability publicly until a patch is available
                                     2. 2. We will provide credit to the researcher who reported the vulnerability (unless you prefer anonymity)
                                        3. 3. We typically wait 30 days after patch release before making vulnerability details public
                                           4. 4. For critical vulnerabilities, we may coordinate with users before public disclosure
                                             
                                              5. ## Security Considerations for Users
                                             
                                              6. ### Model Integrity
                                             
                                              7. Since RabbitRedux is a machine learning model, users should be aware of:
                                             
                                              8. - **Model Poisoning**: Be cautious when training or fine-tuning the model with untrusted data
                                                 - - **Input Validation**: Always validate and sanitize code inputs before classification
                                                   - - **Model Updates**: Keep the model updated to receive security improvements and bias fixes
                                                    
                                                     - ### API Security (if deployed as a service)
                                                    
                                                     - - Use HTTPS/TLS for all API communications
                                                       - - Implement authentication and authorization controls
                                                         - - Rate-limit API endpoints to prevent abuse
                                                           - - Monitor logs for suspicious activity
                                                             - - Sanitize all code inputs to prevent injection attacks
                                                              
                                                               - ### Data Privacy
                                                              
                                                               - - The model processes code samples; ensure compliance with data protection regulations
                                                                 - - Do not use RabbitRedux on sensitive or proprietary code without proper safeguards
                                                                   - - If deploying in production, implement appropriate data retention policies
                                                                    
                                                                     - ### Dependency Security
                                                                    
                                                                     - RabbitRedux depends on several Python packages. We recommend:
                                                                    
                                                                     - - Regularly updating dependencies to patch known vulnerabilities
                                                                       - - Using tools like `pip-audit` to scan for known vulnerabilities in dependencies
                                                                         - - Monitoring security advisories for packages like `transformers`, `torch`, and `fastapi`
                                                                          
                                                                           - ## Security Best Practices for Deployment
                                                                          
                                                                           - ### If Using with FastAPI
                                                                          
                                                                           - - Enable CORS only for trusted origins
                                                                             - - Implement request validation and sanitization
                                                                               - - Use environment variables for sensitive configuration (API keys, etc.)
                                                                                 - - Enable logging and monitoring for audit trails
                                                                                   - - Implement rate limiting to prevent abuse
                                                                                    
                                                                                     - ### If Using with Docker
                                                                                    
                                                                                     - - Build images from trusted base images
                                                                                       - - Scan images for vulnerabilities using tools like Trivy
                                                                                         - - Run containers with minimal privileges (non-root user)
                                                                                           - - Use container security best practices
                                                                                            
                                                                                             - ### General Recommendations
                                                                                            
                                                                                             - - Keep the Python runtime and all dependencies updated
                                                                                               - - Use virtual environments to isolate dependencies
                                                                                                 - - Implement input validation for all external data
                                                                                                   - - Monitor system resources for anomalous behavior
                                                                                                     - - Maintain audit logs of model usage and predictions
                                                                                                      
                                                                                                       - ## Known Security Limitations
                                                                                                      
                                                                                                       - ### Model Behavior
                                                                                                      
                                                                                                       - - The model's classification decisions should not be relied upon as the sole security mechanism
                                                                                                         - - The model may produce false positives or false negatives
                                                                                                           - - Adversarial inputs may fool the classifier
                                                                                                             - - The model is trained on specific datasets and may not generalize to all code types
                                                                                                              
                                                                                                               - ### Data Handling
                                                                                                              
                                                                                                               - - Code samples are processed in memory; ensure sufficient security controls
                                                                                                                 - - API responses may be logged; sanitize sensitive information from code inputs
                                                                                                                   - - The model predictions should be treated as informational rather than definitive
                                                                                                                    
                                                                                                                     - ## Security Advisories
                                                                                                                    
                                                                                                                     - We will publish security advisories for significant vulnerabilities. Check the following for advisories:
                                                                                                                    
                                                                                                                     - - GitHub Security Advisories: https://github.com/canstralian/RabbitRedux/security/advisories
                                                                                                                       - - Release Notes: https://github.com/canstralian/RabbitRedux/releases
                                                                                                                        
                                                                                                                         - ## Contributing to Security
                                                                                                                        
                                                                                                                         - If you would like to help improve the security of RabbitRedux:
                                                                                                                        
                                                                                                                         - - Review code for security vulnerabilities
                                                                                                                           - - Test the model against adversarial inputs
                                                                                                                             - - Suggest security improvements
                                                                                                                               - - Help us understand edge cases and limitations
                                                                                                                                
                                                                                                                                 - ## Security Contact
                                                                                                                                
                                                                                                                                 - **Primary Contact**: canstralian (GitHub)
                                                                                                                                 - **Email**: canstralian@github.com
                                                                                                                                 - **Keybase**: Please contact via email for encrypted communication
                                                                                                                                
                                                                                                                                 - ## Third-Party Dependencies
                                                                                                                                
                                                                                                                                 - RabbitRedux uses the following key dependencies:
                                                                                                                                
                                                                                                                                 - - `transformers` - For model loading and inference
                                                                                                                                   - - `torch` - For deep learning computation
                                                                                                                                     - - `fastapi` - For API deployment
                                                                                                                                       - - `uvicorn` - For ASGI server
                                                                                                                                        
                                                                                                                                         - We monitor these dependencies for security vulnerabilities and update them regularly.
                                                                                                                                        
                                                                                                                                         - ## Acknowledgments
                                                                                                                                        
                                                                                                                                         - We appreciate the security research community and all responsible disclosure reports. Your efforts help make RabbitRedux safer for everyone.
                                                                                                                                        
                                                                                                                                         - ---
                                                                                                                                         
                                                                                                                                         **Last Updated**: January 2026
                                                                                                                                         **Version**: 1.0

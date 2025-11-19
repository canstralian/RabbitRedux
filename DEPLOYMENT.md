# RabbitRedux Deployment Guide

## Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- Git

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development Deployment

Run the development server:

```bash
# Using Flask directly
export FLASK_ENV=development
python -m flask run

# Or using the app.py entry point
python app.py
```

The API will be available at `http://localhost:5000`

## Production Deployment

### Using Gunicorn (Recommended)

```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --threads 2 \
         --timeout 120 \
         --log-level info \
         wsgi:app
```

### Using Docker

1. Build the Docker image:
```bash
docker build -t rabbitredux:latest .
```

2. Run the container:
```bash
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key-here \
  -e FLASK_ENV=production \
  --name rabbitredux \
  rabbitredux:latest
```

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - MODEL_NAME=canstralian/WhiteRabbitNeo
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment

### AWS (EC2)

1. Launch an EC2 instance (t2.medium or larger recommended)
2. Install Docker or Python environment
3. Configure security groups (open port 5000 or use a load balancer)
4. Deploy using Docker or Gunicorn
5. Consider using AWS ECS or EKS for container orchestration

### Google Cloud Platform (Cloud Run)

```bash
gcloud run deploy rabbitredux \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure (Container Instances)

```bash
az container create \
  --resource-group myResourceGroup \
  --name rabbitredux \
  --image rabbitredux:latest \
  --dns-name-label rabbitredux \
  --ports 5000
```

### Heroku

```bash
heroku create rabbitredux
heroku config:set SECRET_KEY=your-secret-key-here
git push heroku main
```

## Kubernetes Deployment

Example Kubernetes manifests in `k8s/`:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Monitoring and Health Checks

- Health check endpoint: `GET /health`
- Metrics endpoint: Available through integration with Prometheus (see monitoring documentation)

## Scaling Considerations

1. **Horizontal Scaling**: Run multiple instances behind a load balancer
2. **Model Caching**: The model is loaded once per worker process
3. **Resource Requirements**: 
   - Minimum: 2 CPU cores, 4GB RAM
   - Recommended: 4 CPU cores, 8GB RAM
   - For high traffic: Consider GPU instances

## Security Checklist

- [ ] Set a strong SECRET_KEY in production
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS appropriately
- [ ] Set up rate limiting (use nginx or application-level)
- [ ] Keep dependencies updated
- [ ] Run security scans regularly
- [ ] Use environment variables for sensitive data
- [ ] Enable logging and monitoring

## Troubleshooting

### Common Issues

1. **Model Loading Fails**
   - Ensure sufficient memory is available
   - Check network connectivity for model download
   - Verify model name is correct

2. **High Memory Usage**
   - Reduce number of workers
   - Consider model quantization
   - Use CPU instead of GPU if necessary

3. **Slow Response Times**
   - Enable caching
   - Increase worker count
   - Use GPU if available
   - Consider batch processing for multiple requests

## Backup and Disaster Recovery

1. **Application Code**: Use Git for version control
2. **Configuration**: Store in version control (excluding secrets)
3. **Models**: Models are pulled from Hugging Face, no backup needed
4. **Logs**: Configure log rotation and backup

## Updates and Maintenance

To update the application:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
# Restart the service
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/canstralian/RabbitRedux/issues
- Documentation: See README.md

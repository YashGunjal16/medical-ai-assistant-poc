# Deployment Guide - Medical AI POC

Complete guide for deploying the Medical AI Assistant on various platforms.

## Render.com Deployment (Recommended)

### Prerequisites
- GitHub account with repository
- Render.com account
- Google API key with Gemini access

### Step-by-Step

1. **Prepare Repository**
   \`\`\`bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   \`\`\`

2. **Connect to Render**
   - Visit https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Select GitHub repository
   - Render auto-detects `render.yaml`

3. **Configure Services**
   Render creates two services:
   - **medical-ai-backend**: FastAPI on port 8000
   - **medical-ai-frontend**: Streamlit on port 8501

4. **Set Environment Variables**
   - Go to Service → Environment
   - Add `GOOGLE_API_KEY`
   - Add `GOOGLE_SEARCH_API_KEY` (optional)

5. **Deploy**
   - Click Deploy
   - Wait 3-5 minutes for services to start
   - Get URLs from dashboard

### Monitoring
- Check logs: Service → Logs
- Monitor CPU/Memory: Service → Metrics
- Restart services if needed

## Docker Deployment (Local/Self-Hosted)

### Using Docker Compose

\`\`\`bash
# Setup
git clone <repo-url>
cd medical_ai_poc
cp .env.example .env
# Edit .env with API keys

# Deploy
docker-compose up -d

# Verify
docker ps
# Should see 3 containers: backend, frontend, chroma

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down
\`\`\`

### Using Docker Hub

\`\`\`bash
# Build
docker build -t medical-ai-poc:latest .

# Push (after docker login)
docker push username/medical-ai-poc:latest

# Run
docker run -p 8000:8000 -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key \
  username/medical-ai-poc:latest
\`\`\`

## AWS Deployment

### Option 1: ECS (Container Orchestration)

\`\`\`bash
# Create ECR repository
aws ecr create-repository --repository-name medical-ai-poc

# Build and push
docker build -t medical-ai-poc .
docker tag medical-ai-poc:latest <account>.dkr.ecr.<region>.amazonaws.com/medical-ai-poc:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/medical-ai-poc:latest

# Create ECS task definition, service, and cluster via AWS console
\`\`\`

### Option 2: EC2 (Virtual Machine)

\`\`\`bash
# Connect to EC2 instance
ssh -i key.pem ec2-user@instance.amazonaws.com

# Install Docker
sudo yum install docker -y
sudo systemctl start docker

# Clone and run
git clone <repo-url>
cd medical_ai_poc
cp .env.example .env
# Edit .env
docker-compose up -d
\`\`\`

## Google Cloud Deployment

### Option 1: Cloud Run

\`\`\`bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/medical-ai-poc

# Deploy
gcloud run deploy medical-ai-poc \
  --image gcr.io/PROJECT_ID/medical-ai-poc \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=your_key
\`\`\`

### Option 2: Compute Engine

\`\`\`bash
# Similar to EC2 - use startup script to install Docker
# Then run docker-compose up -d
\`\`\`

## Heroku Deployment

\`\`\`bash
# Create Heroku app
heroku create medical-ai-poc

# Create Procfile
cat > Procfile << EOF
release: echo "Starting services"
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF

# Set environment variables
heroku config:set GOOGLE_API_KEY=your_key

# Deploy
git push heroku main

# View logs
heroku logs --tail
\`\`\`

## DigitalOcean App Platform

1. Connect GitHub repository
2. DigitalOcean auto-detects Docker files
3. Set environment variables
4. Deploy
5. Get app URL from dashboard

## VPS Deployment (Ubuntu/CentOS)

\`\`\`bash
# SSH into server
ssh user@server.ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone <repo-url>
cd medical_ai_poc

# Setup environment
cp .env.example .env
# Edit .env with API keys

# Deploy
docker-compose up -d

# Nginx reverse proxy (optional)
sudo apt install nginx -y
# Configure nginx to proxy to localhost:8000 and 8501
\`\`\`

## Post-Deployment Tasks

### 1. Initialize Vector Store
\`\`\`bash
# If running in container
docker exec medical-ai-backend python scripts/init_vector_store.py

# If running locally
python scripts/init_vector_store.py
\`\`\`

### 2. Upload Initial PDFs
\`\`\`bash
# Via API
curl -X POST https://your-app.render.com/api/rag/upload-pdf \
  -F "file=@path/to/comprehensive-clinical-nephrology.pdf"

# Or via Streamlit UI
# Navigate to Knowledge Base Management section
\`\`\`

### 3. Configure DNS (if using custom domain)
- Update DNS records to point to deployment
- Configure SSL/TLS certificate (usually auto-handled)

### 4. Set Up Monitoring
- Configure error alerts
- Set up log aggregation
- Monitor API response times

## Performance Optimization

### Caching
- Enable Redis for session caching (optional)
- Cache embedding results
- Cache patient data

### Database Scaling
- Use managed database for production
- Enable read replicas for high traffic
- Consider document partitioning by patient

### Load Balancing
- Use load balancer for multiple instances
- Auto-scale based on CPU/memory
- Distribute traffic evenly

## Backup & Recovery

### Vector Store Backup
\`\`\`bash
# Backup ChromaDB data
docker exec medical-ai-chroma tar -czf - /chroma_data > backup.tar.gz

# Restore
docker exec medical-ai-chroma tar -xzf - < backup.tar.gz
\`\`\`

### Application Backup
\`\`\`bash
# Backup logs and data
tar -czf backup.tar.gz app/data logs

# Version control important files
git commit -m "Backup before deployment"
\`\`\`

## Security Checklist

- [ ] API keys in environment variables only
- [ ] .env file in .gitignore
- [ ] HTTPS enabled for all endpoints
- [ ] CORS configured appropriately
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Logging all interactions
- [ ] Regular security updates
- [ ] Backup and disaster recovery plan
- [ ] Data privacy compliance (HIPAA if needed)

## Troubleshooting Deployment

### Services won't start
- Check logs: `docker-compose logs`
- Verify environment variables: `docker-compose config`
- Check port availability: `lsof -i :8000`

### API connection errors
- Verify backend URL in Streamlit config
- Check network connectivity
- Review CORS settings

### Performance issues
- Monitor CPU/memory usage
- Check API rate limits
- Verify database queries

### Memory leaks
- Check for unclosed connections
- Monitor ChromaDB memory usage
- Review log file sizes

## Scaling Considerations

### Current Architecture Limits
- Single-instance backend
- In-memory ChromaDB
- Local file logging

### Scaling Solutions
1. **Horizontal**: Load balancer + multiple backend instances
2. **Vertical**: Larger server with more resources
3. **Database**: Managed ChromaDB cloud service
4. **Caching**: Redis for session/embedding cache
5. **Async**: Celery for long-running tasks

## Cost Estimation

### Render.com (Free Tier)
- Backend: Free (with cold starts)
- Frontend: Free (with cold starts)
- Total: $0/month

### AWS
- EC2: $10-50/month
- ECS: $0 (pay for compute only)
- Data transfer: $0-20/month

### Google Cloud
- Cloud Run: $1-10/month
- Compute Engine: $20-50/month

### DigitalOcean
- App Platform: $15-50/month
- Droplet: $5-40/month

---

For issues or questions, check logs and consult platform-specific documentation.

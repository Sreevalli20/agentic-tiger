# Deployment Guide

## Prerequisites

### Required
- Python 3.12+ (for local development)
- Node.js 18+ (for frontend development)
- Docker and Docker Compose (for containerized deployment)
- TigerGraph instance (local or cloud)
- Google AI Studio API key (free tier available)

### Optional
- Render account (for backend deployment)
- Vercel account (for frontend deployment)
- TigerGraph Cloud account

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/Sreevalli20/agentic-tiger.git
cd agentic-tiger
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# LLM Configuration
LLM_PROVIDER=google
LLM_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-1.5-flash

# TigerGraph Configuration
TG_HOST=localhost
TG_PORT=14240
TG_SECRET=your_tigergraph_secret_here
TG_GRAPHNAME=graphrag_hackathon

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 5. Start Backend
```bash
cd backend
python -m app.main
```

Backend runs on `http://localhost:8000`

### 6. Start Frontend
```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

## Docker Deployment

### Quick Start
```bash
docker-compose up -d
```

This starts:
- Backend on `http://localhost:8000`
- Frontend on `http://localhost:80`

### Docker Configuration

#### Backend Dockerfile
- Base image: `python:3.12-slim`
- System dependencies: gcc, g++, curl
- Python dependencies from `requirements.txt`
- Health check via `/api/health`
- Production server: Gunicorn

#### Frontend Dockerfile
- Base image: `node:18-alpine` (build), `nginx:alpine` (serve)
- Multi-stage build for optimization
- Static files served by Nginx
- Environment variable for API URL

#### Docker Compose
- Backend and frontend services
- Shared network for communication
- Volume mounts for data persistence
- Health checks and restart policies
- Environment variable configuration

### Docker Commands

#### Build and Start
```bash
docker-compose up -d --build
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Stop Services
```bash
docker-compose down
```

#### Restart Services
```bash
docker-compose restart
```

#### Clean Up
```bash
docker-compose down -v  # Removes volumes
```

## Cloud Deployment

### Backend on Render

#### 1. Prepare for Render
```bash
# Ensure backend/Dockerfile is production-ready
# Ensure .env variables are set in Render dashboard
```

#### 2. Create Render Service
1. Go to Render Dashboard
2. Create new "Web Service"
3. Connect GitHub repository
4. Set build context: `backend`
5. Set Dockerfile path: `Dockerfile`
6. Configure environment variables:
   - `LLM_PROVIDER=google`
   - `LLM_API_KEY=your_key`
   - `TG_HOST=your_tigergraph_host`
   - `TG_SECRET=your_secret`
   - `TG_GRAPHNAME=graphrag_hackathon`
7. Deploy

#### 3. Environment Variables
Set these in Render dashboard:
- `PORT=8000` (Render sets this automatically)
- `APP_HOST=0.0.0.0`
- `CORS_ORIGINS=https://your-frontend-domain.vercel.app`

#### 4. Health Check
Render automatically uses the health check from Dockerfile.

### Frontend on Vercel

#### 1. Prepare for Vercel
```bash
# Build frontend locally first
cd frontend
npm run build
```

#### 2. Create Vercel Project
1. Go to Vercel Dashboard
2. Create new project
3. Import GitHub repository
4. Set root directory: `frontend`
5. Configure build settings:
   - Framework: Vite
   - Build command: `npm run build`
   - Output directory: `dist`
6. Add environment variable:
   - `VITE_API_BASE_URL=https://your-backend-domain.onrender.com`
7. Deploy

#### 3. Domain Configuration
Vercel provides a default domain. Configure custom domain if needed.

### TigerGraph Cloud

#### 1. Create TigerGraph Cloud Instance
1. Go to TigerGraph Cloud
2. Create new graph
3. Choose configuration (free tier available)
4. Note connection details:
   - Host
   - Port (usually 14240)
   - Secret
   - Graph name

#### 2. Configure Backend
Update backend `.env` with TigerGraph Cloud credentials:
```bash
TG_HOST=your-cloud-instance.i.tgcloud.io
TG_PORT=14240
TG_SECRET=your_secret
TG_GRAPHNAME=graphrag_hackathon
```

#### 3. Run Ingestion
```bash
cd backend
python -m app.tigergraph.ingestion
```

## Data Ingestion

### Initial Ingestion
```bash
cd backend
python -m app.tigergraph.ingestion
```

This:
1. Loads corpus from `hackathon-resources/corpus/corpus.jsonl`
2. Parses documents and extracts entities
3. Creates TigerGraph schema
4. Loads vertices and edges
5. Validates and reports statistics

### Ingestion Validation
Check ingestion results:
```bash
# Via API
curl http://localhost:8000/api/health

# Via TigerGraph console
# Run: SELECT COUNT(*) FROM Event
```

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "tigergraph_connected": true,
  "vector_db_connected": true,
  "llm_configured": true
}
```

### Logs
```bash
# Docker logs
docker-compose logs -f backend

# Application logs (if running locally)
# Check backend stdout/stderr
```

### Metrics
Access metrics dashboard at `/metrics` in frontend after running benchmark.

## Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Change port in .env
APP_PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill
```

#### TigerGraph Connection Failed
```bash
# Check TigerGraph is running
# Verify credentials in .env
# Test connection:
python -c "from pytigergraph import TigerGraphConnection; conn = TigerGraphConnection(host='your_host', password='your_secret'); print(conn.echo())"
```

#### Vector DB Issues
```bash
# Clear vector DB
rm -rf data/vector_db

# Rebuild on next startup
```

### Frontend Issues

#### API Connection Failed
```bash
# Check VITE_API_BASE_URL in .env
# Verify backend is running
# Check CORS configuration
```

#### Build Failed
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Docker Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build

# Check disk space
df -h
```

#### Volume Issues
```bash
# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

## Performance Optimization

### Backend
- Use Gunicorn with multiple workers for production
- Enable connection pooling for database connections
- Cache embeddings in vector DB
- Use async operations for I/O

### Frontend
- Enable code splitting
- Optimize bundle size
- Use CDN for static assets
- Implement lazy loading for charts

### Database
- Create indexes on frequently queried fields
- Use connection pooling
- Monitor query performance
- Scale TigerGraph instance if needed

## Security

### Environment Variables
- Never commit `.env` file
- Use different secrets for dev/staging/prod
- Rotate secrets regularly
- Use secret management service (e.g., Render Secrets)

### API Security
- Enable HTTPS in production
- Configure CORS for specific domains
- Rate limit API endpoints
- Validate all inputs

### Data Security
- Encrypt sensitive data at rest
- Use secure connections for databases
- Implement authentication if needed
- Regular security audits

## Backup and Recovery

### Data Backup
```bash
# Backup vector DB
tar -czf vector_db_backup.tar.gz data/vector_db

# Backup evaluation results
tar -czf evaluation_backup.tar.gz evaluation/results
```

### TigerGraph Backup
Use TigerGraph Cloud backup features or export GSQL schema.

### Recovery
```bash
# Restore vector DB
tar -xzf vector_db_backup.tar.gz -C data/

# Restore evaluation results
tar -xzf evaluation_backup.tar.gz -C evaluation/
```

## Scaling

### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use shared vector DB (e.g., ChromaDB Cloud)
- Use shared TigerGraph instance
- Implement session affinity if needed

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Scale TigerGraph instance
- Optimize database queries
- Cache frequently accessed data

## Cost Optimization

### LLM Costs
- Use free tier Google Gemini
- Implement response caching
- Optimize prompt length
- Batch requests when possible

### Infrastructure Costs
- Use appropriate instance sizes
- Auto-scale based on traffic
- Use spot instances for non-critical workloads
- Monitor and optimize resource usage

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Review and rotate secrets
- Monitor error rates
- Check disk space usage
- Review benchmark results

### Updates
```bash
# Update backend
cd backend
pip install -r requirements.txt --upgrade

# Update frontend
cd frontend
npm update
```

### Monitoring
- Set up uptime monitoring
- Configure error tracking (e.g., Sentry)
- Monitor resource usage
- Review performance metrics

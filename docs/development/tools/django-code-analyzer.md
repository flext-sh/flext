# 🐍 Django Code Analyzer

> **Advanced Python Code Quality Analysis Platform**

A modern Django-based web application for comprehensive Python code analysis with automatic package discovery, interactive visualizations, and detailed quality metrics.

## 🚀 Key Features

### 📦 **Automatic Package Discovery**

- **Smart Detection**: Automatically discovers installed Python packages
- **Source Prioritization**: Prioritizes source installations over wheel packages
- **Package Classification**: Categorizes packages as source, wheel, system, or local
- **Analyzable Filtering**: Filters packages suitable for code analysis

### 🔍 **Comprehensive Code Analysis**

- **Security Scanning**: Uses Bandit for vulnerability detection
- **Dead Code Detection**: Identifies unused code with Vulture
- **Duplicate Code Analysis**: Finds code duplication patterns
- **Complexity Metrics**: Calculates cyclomatic complexity with Radon
- **Quality Scoring**: 0-100 scoring system with grade classification

### 📊 **Interactive Dashboard**

- **Real-time Charts**: Chart.js powered visualizations
- **Quality Trends**: Track quality metrics over time
- **Security Distribution**: Visual breakdown of security issues
- **Project Comparison**: Side-by-side flx_project analysis
- **Radar Charts**: Multi-dimensional quality assessment

### 🎯 **No Authentication Required**

- **Simplified Access**: No user management overhead
- **Open Analysis**: All projects and packages accessible
- **Quick Setup**: Ready to use out of the box

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9+
- Django 5.0+
- PostgreSQL (optional, SQLite by default)

### Quick Start

#### Option 1: Using Startup Script (Recommended)

```bash
git clone <repository>
cd dc-code-analyzer
./start_server.sh
```

#### Option 2: Manual Setup

1. **Clone and Setup**

   ```bash
   git clone <repository>
   cd dc-code-analyzer
   pip install -r requirements.txt
   pip install sarif-om jschema-to-python  # Additional dependencies
   ```

2. **Database Setup**

   ```bash
   python manage.py migrate
   ```

3. **Start Server with Auto-reload**

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. **Access Application**

   ```
   🌐 Main Dashboard: http://localhost:8000/
   📦 Package Discovery: http://localhost:8000/packages/
   📊 Admin Interface: http://localhost:8000/REDACTED_LDAP_BIND_PASSWORD/
   ```

## 📁 Project Structure

```
dc_code_analyzer/
├── analyzer/                    # Core analysis engine
│   ├── models.py               # Data models
│   ├── package_discovery.py   # Package discovery system
│   └── migrations/            # Database migrations
├── dashboard/                  # Web interface
│   ├── views.py               # Dashboard views
│   ├── charts.py              # Chart data endpoints
│   └── urls.py                # URL routing
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── dashboard/             # Dashboard templates
│   └── packages.html          # Package discovery interface
├── static/                     # Static files
├── requirements.txt           # Python dependencies
└── manage.py                  # Django management
```

## 🐍 Package Discovery System

### **Automatic Detection**

The system automatically discovers Python packages using:

- `importlib.metadata` (Python 3.8+)
- `pkg_resources` (fallback)

### **Package Types**

- **Source**: Development installations (`pip install -e`)
- **Wheel**: Standard installations
- **System**: System-wide packages
- **Local**: Custom flx_project directories

### **Smart Filtering**

- Excludes common utility packages (pip, setuptools, etc.)
- Prioritizes packages with analyzable Python code
- Estimates package size by Python file count

## 📊 Analysis Features

### **Quality Metrics**

- **Overall Score**: Composite quality rating (0-100)
- **Complexity Score**: Code complexity assessment
- **Security Score**: Vulnerability analysis
- **Maintainability Score**: Code maintainability rating
- **Documentation Score**: Docstring coverage
- **Duplication Score**: Code duplication analysis

### **Issue Detection**

- **Security Issues**: HIGH/MEDIUM/LOW/INFO severity levels
- **Dead Code**: Unused functions, classes, variables, imports
- **Code Duplicates**: Similar code blocks across files
- **Complex Functions**: High cyclomatic complexity warnings

### **Reporting**

- **Visual Charts**: Interactive Chart.js visualizations
- **Trend Analysis**: Quality metrics over time
- **Comparative Analysis**: Project-to-flx_project comparison
- **Detailed Reports**: File-level analysis results

## 🖥️ Web Interface

### **Dashboard Pages**

#### **Main Dashboard** (`/dashboard/`)

- Project overview statistics
- Recent analysis activity
- Quick action buttons
- Interactive charts

#### **Projects List** (`/dashboard/projects/`)

- All analyzed projects
- Search and filter capabilities
- Quality score indicators
- Analysis history

#### **Package Discovery** (`/dashboard/packages/`)

- Discovered Python packages
- Package type filtering
- Search functionality
- One-click flx_project creation

#### **Project Details** (`/dashboard/projects/<id>/`)

- Detailed flx_project information
- Analysis session history
- Quality metrics breakdown
- Issue summaries

### **Interactive Charts**

1. **Quality Trends**: Line chart showing quality evolution
2. **Security Distribution**: Doughnut chart of security issues
3. **Project Comparison**: Bar chart comparing projects
4. **Quality Radar**: Multi-dimensional quality assessment
5. **Issues Timeline**: Stacked area chart of issues over time
6. **Complexity Distribution**: Histogram of complexity ranges

## 🔧 API Endpoints

### **Chart Data APIs**

```
GET /dashboard/charts/summary-stats/          # Dashboard statistics
GET /dashboard/charts/quality-trends/         # Quality trends data
GET /dashboard/charts/security-issues/        # Security distribution
GET /dashboard/charts/projects-comparison/    # Project comparison
GET /dashboard/charts/quality-radar/          # Radar chart data
GET /dashboard/charts/issues-timeline/        # Issues timeline
GET /dashboard/charts/complexity-distribution/ # Complexity histogram
```

### **Package Discovery APIs**

```
GET /dashboard/packages/                      # Package discovery interface
POST /dashboard/packages/create/              # Create flx_project from package
GET /dashboard/packages/refresh/              # Refresh package cache
```

### **Project Management APIs**

```
GET /dashboard/projects/                      # Project list
POST /dashboard/projects/create/              # Create new flx_project
GET /dashboard/projects/<id>/                 # Project details
POST /dashboard/projects/<id>/analyze/        # Start analysis
```

## 💡 Usage Examples

### **Create Project from Package**

1. Navigate to **Python Packages** in sidebar
2. Search or filter packages
3. Click **Create Project** on desired package
4. System automatically configures flx_project settings

### **Start Analysis**

1. Go to flx_project details page
2. Click **Start Analysis** button
3. Monitor analysis progress
4. Review results in charts and reports

### **View Trends**

1. Access main dashboard
2. Review quality trends chart
3. Filter by time period (7d, 30d, 90d, 365d)
4. Compare multiple projects

## ⚙️ Configuration

### **Analysis Settings**

Configure analysis parameters in flx_project settings:

- **Security Analysis**: Enable/disable Bandit scanning
- **Dead Code Detection**: Enable/disable Vulture analysis
- **Duplicate Detection**: Enable/disable duplicate code scanning
- **Complexity Threshold**: Set complexity warning levels
- **Similarity Threshold**: Set duplicate detection sensitivity

### **Package Discovery**

The package discovery system can be customized:

- **Skip Packages**: Configure packages to exclude
- **Source Priority**: Prioritize source installations
- **Size Filtering**: Filter by minimum package size

## 🔍 Troubleshooting

### **Common Issues**

1. **Package Discovery Not Working**

   - Check Python environment
   - Verify package installations
   - Try manual refresh

2. **Analysis Fails**

   - Verify source code accessibility
   - Check file permissions
   - Review error logs

3. **Charts Not Loading**
   - Check JavaScript console
   - Verify Chart.js CDN
   - Refresh browser cache

### **Debug Mode**

Enable Django debug mode for detailed error information:

```python
# settings.py
DEBUG = True
```

## 📈 Performance Tips

1. **Large Projects**: Analysis time scales with flx_project size
2. **Package Filtering**: Use filters to focus on relevant packages
3. **Cache Management**: Refresh package cache periodically
4. **Database Cleanup**: Archive old analysis sessions

## 🛡️ Security Considerations

- **No Authentication**: Application is open by default
- **File Access**: Analyzer can read any accessible Python files
- **Network Access**: CDN dependencies for charts and styling
- **Database**: Contains analysis results and flx_project metadata

## 🔄 Updates & Maintenance

### **Regular Tasks**

- **Package Refresh**: Update package discovery cache
- **Database Cleanup**: Remove old analysis sessions
- **Log Rotation**: Manage application logs
- **Dependency Updates**: Keep packages current

### **Monitoring**

- **Analysis Success Rate**: Track failed analyses
- **Performance Metrics**: Monitor response times
- **Storage Usage**: Monitor database growth
- **Error Logs**: Review application errors

## 📝 Development

### **Adding New Analysis Tools**

1. Create analyzer module in `analyzer/`
2. Add model fields for results
3. Update analysis pipeline
4. Create visualization components

### **Custom Charts**

1. Add chart endpoint in `dashboard/charts.py`
2. Register URL in `dashboard/urls.py`
3. Create frontend component
4. Add to dashboard template

## 📚 Additional Resources

- **Django Documentation**: <https://docs.djangoproject.com/>
- **Chart.js Guide**: <https://www.chartjs.org/docs/>
- **Bandit Security**: <https://bandit.readthedocs.io/>
- **Code Analysis Tools**: Vulture, Radon, Pylint

## 🤝 Support

For issues, suggestions, or contributions:

1. Check existing documentation
2. Review troubleshooting section
3. Examine application logs
4. Test with sample projects

---

**Django Code Analyzer** - Making Python code quality analysis accessible and actionable.

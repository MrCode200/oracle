# Oracle Financial Analysis Platform  
  
## 📊 Overview  
  
The Oracle Financial Analysis Platform is a sophisticated algorithmic trading system that combines data fetching, technical analysis, evolutionary optimization, and database management. The platform is designed to optimize financial trading strategies through genetic algorithms and provides a complete framework for backtesting and parameter tuning.  
  
## 🏗️ System Architecture  
  
The Oracle platform follows a layered architecture with clear separation of concerns across multiple components:  
  
### Core Components  
- **Application Layer**: Main application initialization and command-line interface  
- **Data Pipeline**: Market data fetching and processing from Yahoo Finance 
- **Analysis Engine**: Technical indicators (Ichimoku, MACD, RSI) with plugin system  
- **Optimization Engine**: Evolutionary algorithm for parameter tuning (WIP. Will be added in the Future)
- **Database Layer**: MySQL with SQLAlchemy ORM for data persistence
  
## 🔧 Prerequisites & Setup  
  
### Required Dependencies  
  
The platform requires Python 3.x with the following key dependencies:  
  
- **Data Processing**: pandas (2.2.3), numpy (2.1.3), pandas_ta (0.3.14b0)  
- **Logic**: apscheduler (~3.11.0)
- **Database**: SQLAlchemy (~2.0.36)
- **CLI**: typer['all'] (~0.15.1), prompt-toolkit(~3.0.48), rich (~13.9.4), pydantic (~2.10.4)
- **Testing**: pytest (~8.3.3)  
  
#### Database Configuration (MySQL)
  
Create/Edit the configuration file at `backend/config/config.json` with the following structure:  
  
```json  
{  
  "DB_CONFIG": {  
    "host": "localhost",  
    "user": "your_username",  
    "password": "your_password",  
    "database": "oracle"  
  },  
  "LOG_CONFIG": {  
    "level": "INFO",  
    "path": "logs/oracle.log"  
  }  
}  
```
  
#### Database Models  
  
The system manages four core entities:  
- **Profile**: Trading profiles with wallet and strategy settings  
- **Trading Components**: [Technical indicators | Strategies | Patterns | AiComponents] with parameters and performance metrics. (Contains Simple news AI)
- **Plugin**: Strategy plugins with configurations  
- **Order**: Trading orders with type, ticker, quantity, and price information
  
### Installation Steps  
  
1. **Install Python Dependencies**:  
   ```bash  
   pip install poetry
   ```
   Inside Oralce/backend:
   ```bash
   poetry install
   ```  
  
2. **Setup MySQL Database**:  
   - Install MySQL Server  
   - Create a database user with appropriate permissions  
   - Configure connection parameters in `backend/config/config.json`  
  
3. **Initialize Application**:
   When inside 'poetry shell' using `oracle` starts the cli and initlizes the app
  
## 🧮 Technical Indicators  
  
The platform implements several sophisticated technical indicators:  
  
### Available Indicators 
- **MACD**: Moving Average Convergence Divergence
- **SMA**: Simple Moving Average

And many more...

Each indicator inherits from a base class and implements standardized methods for evaluation and backtesting.
  
## 🧬 Evolutionary Algorithm  
  
The platform's core strength lies in its evolutionary optimization capabilities. The genetic algorithm optimizes parameters for financial indicators through multiple generations:  
  
### Key Features  
- **Population-based optimization**: Evolves parameter sets over generations  
- **Mutation and crossover**: Generates offspring with improved characteristics  
- **Performance-based selection**: Retains top performers for reproduction  
- **Configurable parameters**: Adjustable population size, generations, and mutation rates
  
`❗ Combination of some Settings may result in Overfitting!`

`❗ WIP`
  
## 📈 Data Sources  
  
The platform integrates with multiple external data sources:  
  
### Supported APIs  
- **Yahoo Finance**: News for Ai News Evaluator (Scrappy)
- **Binance**: For Fetching Trading Data and Trading with Broker `❗ WIP`
  
### Data Processing Pipeline  
1. **Data Fetching**: Retrieves historical market data  
2. **Data Modification**: Processes and validates data integrity  
3. **Interval Determination**: Optimizes data granularity  
4. **Analysis Integration**: Feeds processed data to indicators 
  
## 🧪 Testing Framework  
  
The platform includes comprehensive testing coverage:  
  
### Test Structure  
- `test_algorithms/`: Tests for technical indicators and optimization  
- `test_api/`: Tests for data fetching and API integration  
- `test_database/`: Tests for database operations and models  
- `test_exceptions/`: Tests for error handling and edge cases

`❗ Not Finished`

### Running Tests  
```bash  
pytest backend/tests/  
```  
  
## 🎯 Usage Examples  
  
### Basic Application Initialization  
The application starts with the `init_app()` function after running 
```bash
poetry shell
oracle
```
command which orchestrates system initialization:  
  
1. **Logger Setup**: Configures application logging  
2. **Indicator Registration**: Loads all technical indicators  
3. **Service Initialization**: Starts database services  
4. **Interface Setup**: Activates command-line interface 
  
### Database Operations  
The platform provides comprehensive CRUD operations for all entities:  
  
- **Profile Management**: Create, read, update, delete trading profiles  
- **Order Management**: Track trading orders with timestamps  
- **Plugin Configuration**: Manage strategy plugins and settings  
- **Indicator Tracking**: Monitor indicator performance and parameters 
  
## 📋 Developer Notes  
  
### Important Notes  
1. **NOTE**: `❗ This isn't a finilized Version and is still strongly under development! `
  
2. **Trading Frequency**: The current implementation may run trading operations every 20 seconds for development Purposes. This can be adjusted in the strategy settings later.  
      
3. **Parameter Optimization**: The evolutionary algorithm is not yet implemented!  
  
4. **External API Limits**: Binance API Endpoints have limits, which we cannot bypass!
    
5. **Testing Coverage**: Not everything is covered by tests yet!

6. **Frontend**: To Date, The backend has to be written first, so no code availalbe currently!
  
### Security Notes  
  
- **Database Credentials**: Never commit database credentials to version control  
- **API Keys**: Store external API keys securely and rotate them regularly  
- **Input Validation**: All user inputs are validated before database operations
-   
---  
  
*For more detailed implementation guides and advanced usage scenarios, visit [https://deepwiki.com/MrCode200/oracle](https://deepwiki.com/MrCode200/oracle)*  
`❗ The detailed Documentation is written by AI, and not all is covered correctly (~95% correct)! (Most of the Information is correct though)`
  
## Notes  
    
The evolutionary algorithm implementation is particularly noteworthy, providing a robust framework for parameter optimization that can be applied to various financial indicators and trading strategies. The database layer offers comprehensive CRUD operations with proper error handling and transaction management, ensuring data integrity throughout the application lifecycle. To see the semi-developmt code, visit [miniOracleAlpha](https://github.com/kian19955/miniOracleAlpha) Repository under /Optimization

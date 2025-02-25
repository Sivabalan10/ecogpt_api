# EcoGPT API 
API DOCUMENTAION LINK - [OPEN](https://qrkode.link/vjFJfQ)

## Overview

EcoGPT API is an AI-powered solution designed to tackle inefficiencies in campus energy consumption. The API provides a platform for real-time tracking, personalized energy-saving strategies, and gamified engagement to promote sustainability on campus. Developed during the HappyFox Hackathon, EcoGPT API aims to enhance awareness, engagement, and fair participation in energy-saving efforts.

## Key Features

- **Real-time Energy Tracking**: Monitor campus energy consumption in real-time.
- **Personalized Challenges**: Generate tailored sustainability challenges for users.
- **Gamified Engagement**: Reward eco-friendly actions through a gamified application.
- **AI-Powered Insights**: Utilize AI to analyze energy habits and provide actionable insights.

## Problems Tackled

- **Inefficient Energy Consumption**: Lack of awareness and engagement leads to wastage and high costs.
- **No Effective System**: Absence of a system to motivate students, personalize strategies, or ensure fair participation.
- **Sustainability Culture**: Promote a culture of energy efficiency and sustainability on campus.

## Technologies Used

- **Frontend**: Flutter (Mobile Application)
- **Backend**: Flask (API Modules)
- **Database**: SQL
- **Documentation**: Index.js (API Documentation Page)

## Installation and Setup

### Prerequisites

- Node.js
- Flask
- SQL Database
- Flutter SDK

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Sivabalan10/ecogpt_api.git
   cd ecogpt-api
   ```

2. **Install Dependencies**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

3. **Set Up Database**
   - Create a SQL database and update the configuration in `config.py`.

4. **Run the API**
   ```bash
   flask run
   ```

5. **View API Documentation**
   - Navigate to `index.js` to view the API documentation page.

## Usage

### API Endpoints

- **GET /energy-data**: Retrieve real-time energy consumption data.
- **POST /challenge**: Generate a personalized energy-saving challenge.
- **POST /reward**: Reward a user for completing a challenge.

### Example Request

```bash
curl -X GET http://localhost:5000/energy-data
```

### Example Response

```json
{
  "timestamp": "2023-10-01T12:00:00Z",
  "energy_consumption": 1234.56,
  "campus": "Main Campus"
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSEe) file for details.

## Disclaimer

This is copyrighted code. We encourage you to use and adapt this code for your own projects, but please provide proper attribution.

## Future Plans

We plan to implement EcoGPT API in colleges and universities to promote energy efficiency and sustainability. Stay tuned for updates and new features!

## Contact

For any inquiries, please contact us at [sivabalan10122003@gmail.com]

---

**EcoGPT API Version 0.0.1**  
Developed during the HappyFox Hackathon  
Copyright © 2025 Your Z_axis / team_no: 31. All rights reserved.

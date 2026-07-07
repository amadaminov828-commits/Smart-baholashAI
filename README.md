# Smart Baholash AI

> Automated Property and Asset Valuation Platform | Платформа автоматизированной оценки имущества и активов

---

### Project Status / Статус проекта
![Status](https://img.shields.io/badge/Status-In%20Development%20%2F%20MVP-orange?style=for-the-badge&logo=git)

---

## Language Selection / Выбор языка

Please select your preferred language below: / Пожалуйста, выберите предпочитаемый язык ниже:

---

<details>
<summary><b>🇬🇧 English Version</b></summary>
<br>

### 📄 About
**Smart Baholash AI** is an intelligent, automated platform designed for property and asset valuation. By leveraging advanced Artificial Intelligence (AI) models, Optical Character Recognition (OCR), and market scraping capabilities, the system automates document ingestion, compares parameters with real-time market data, and generates official, compliant valuation reports.

#### Key Features:
* **AI-Powered Analysis**: Integrated with Google Gemini API for deep asset evaluation and description generation.
* **Document Processing & OCR**: Automatically extracts details from scans and PDFs (using EasyOCR & PyMuPDF).
* **Automated Template Ingestion**: Fills Microsoft Word (`.docx`) template reports with precision (using `python-docx` and `docxtpl`) and exports to PDF.
* **Security & Verification**: Signs generated reports with digital signatures, QR codes for verification, and digital seals.
* **Scraping Engine**: Automatic real-time market data retrieval for real estate and vehicles.

---

### 🛠️ Tech Stack

#### Frontend
* **Core**: Next.js 16 (React 19), TypeScript
* **Styling**: TailwindCSS v4
* **Animation**: Framer Motion (for smooth micro-animations and transitions)
* **API Client**: Axios
* **Icons**: Lucide React

#### Backend
* **Core**: Django 6, Django REST Framework (DRF)
* **Database**: PostgreSQL (Production), SQLite (Local Development)
* **Auth**: Django REST Framework Simple JWT (JSON Web Tokens)

#### AI & Document Processing
* **Generative AI**: `google-genai` (Google Gemini SDK)
* **OCR**: EasyOCR, PyTesseract
* **PDF/Word Processing**: PyMuPDF (fitz), PyPDF2, `python-docx`, `docxtpl`, `docx2pdf`
* **Computer Vision**: OpenCV, Pillow
* **Math & Scientific**: NumPy, SymPy, SciPy

---

### 🚀 Getting Started

#### Prerequisites
* Node.js (v18+)
* Python (v3.10+)

#### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file (refer to `.env.example` if available).
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the server:
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

</details>

---

<details>
<summary><b>🇷🇺 Русская версия</b></summary>
<br>

### 📄 О проекте
**Smart Baholash AI** — это интеллектуальная автоматизированная платформа для оценки недвижимости и различных активов. Используя передовые модели искусственного интеллекта (ИИ), распознавание текста (OCR) и парсинг рыночных данных, система автоматизирует ввод документов, сравнивает параметры с реальными рыночными показателями и генерирует официальные отчеты об оценке в соответствии с регламентом.

#### Ключевые функции:
* **Анализ на базе ИИ**: Интеграция с Google Gemini API для углубленной оценки активов и генерации описаний.
* **Обработка документов и OCR**: Автоматическое извлечение данных из сканов и PDF (с использованием EasyOCR и PyMuPDF).
* **Автоматическое заполнение шаблонов**: Точное заполнение отчетов в формате Word (`.docx`) на основе шаблонов (с помощью `python-docx` и `docxtpl`) и экспорт в PDF.
* **Безопасность и проверка**: Подпись сгенерированных отчетов цифровыми подписями, нанесение QR-кодов для верификации и цифровых печатей.
* **Мониторинг рынка**: Автоматический сбор актуальных рыночных объявлений о недвижимости и транспортных средствах.

---

### 🛠️ Стек технологий

#### Frontend
* **Ядро**: Next.js 16 (React 19), TypeScript
* **Стилизация**: TailwindCSS v4
* **Анимации**: Framer Motion (для плавных микровзаимодействий и переходов)
* **Клиент API**: Axios
* **Иконки**: Lucide React

#### Backend
* **Ядро**: Django 6, Django REST Framework (DRF)
* **База данных**: PostgreSQL (Production), SQLite (Локальная разработка)
* **Аутентификация**: DRF Simple JWT (JSON Web Tokens)

#### ИИ и Обработка документов
* **Генеративный ИИ**: `google-genai` (Google Gemini SDK)
* **OCR**: EasyOCR, PyTesseract
* **Работа с PDF/Word**: PyMuPDF (fitz), PyPDF2, `python-docx`, `docxtpl`, `docx2pdf`
* **Компьютерное зрение**: OpenCV, Pillow
* **Математика и вычисления**: NumPy, SymPy, SciPy

---

### 🚀 Быстрый старт

#### Требования
* Node.js (версия 18+)
* Python (версия 3.10+)

#### Настройка Backend
1. Перейдите в папку backend:
   ```bash
   cd backend
   ```
2. Создайте и активируйте виртуальное окружение Python:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Создайте файл `.env` и настройте переменные окружения.
5. Выполните миграции БД:
   ```bash
   python manage.py migrate
   ```
6. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

#### Настройка Frontend
1. Перейдите в папку frontend:
   ```bash
   cd frontend
   ```
2. Установите пакеты:
   ```bash
   npm install
   ```
3. Запустите сервер разработки:
   ```bash
   npm run dev
   ```

</details>

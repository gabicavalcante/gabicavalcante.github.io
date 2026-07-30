+++
title = "Curriculum"
date = "2026-07-30"
+++

Hi! My name is Gabi Cavalcante. 
I’m a full-stack engineer and tech lead with 9+ years of software engineering experience, including 5+ years leading Python/Django SaaS platform teams on Azure. I combine hands-on full-stack delivery with engineering leadership across data platform, infrastructure, and security/compliance work.

I've been spending a lot of time thinking about API design, PostgreSQL performance, cloud infrastructure, observability, and how to build software that stays maintainable as teams grow.

# Positions

### – Vinta Software

| Title | Start |
| --- | --- |
| Tech Lead | 09/2021 |

**Technologies**: Python, Django, React, PostgreSQL, Azure, Celery, Terraform, GitHub Actions, Pytest.

I work at [Vinta Software](https://www.vinta.com.br/), where I lead the Data Platform and Platform/Infrastructure team, focusing on API orchestration, data ingestion, and platform security and reliability. Before this team I led a full-stack App Squad building with Django and React, with my own focus on the backend architecture.

I own the API architecture for integrations with multiple external systems, including direct trademark office integrations, to extract and normalize global trademark data at scale. On the performance side, I optimized PostgreSQL queries on a 25M-row table, cutting a timing-out query to ~54 seconds through histogram-based rewrites and keyset pagination.

I also drove the technical evidence and architecture documentation for our SOC 2 Type II certification and for an enterprise client security review, covering access lifecycle, audit logging, and Azure architecture diagrams. More recently I built an AI-assisted code review skill to catch Django migrations that risk production downtime or table locks before merge.

Leading the team is the other half of the job: 1:1s, career development conversations, and mentoring; partnering with Product and Design on roadmap priorities, technical feasibility, and delivery timelines; running incident management and post-incident reviews for production issues; and upholding engineering practices like TDD, pair programming, and structured code review across the team.

---

### – Stone

| Title | Start | End |
| --- | --- | --- |
| Software Engineer | 10/2020 | 08/2021 |

**Technologies**: Python, Flask Framework, FastAPI, Node.js, GCP (BigQuery, Cloud Functions, Cloud Run), Azure Pipelines, MongoDB, Postgres, MySQL.

I worked on the Governance team at [Stone](https://www.stone.com.br/), building developer-experience tooling to ensure compliance with regulatory bodies. Much of the work was automating manual processes and strengthening controls, so the internal developer tools would hold up as the company scaled.

---

### – Cloudia

| Title | Start | End |
| --- | --- | --- |
| Software Engineer | 03/2020 | 09/2020 |

**Technologies**: Python, Flask Framework, FastAPI, Golang, Redis Queue, Mysql, Pipelines CI/CD, Pytest.

At Cloudia we built an intelligent virtual assistant for medical clinics. I specifically worked with the chatbot and creating solutions focusing in tests and stability, and my challenge there was to optimize the data processing and the transfer of a large amount of data between the services.

I worked mostly with Python, and web frameworks like [Flask](http://flask.palletsprojects.com) and [FastAPI](http://fastapi.tiangolo.com), but I also built a [chatbot load testing in Golang](https://github.com/gabicavalcante/chatbot-load-testing), to simulate many users sending messages to a bot and register a few metrics (CPU, memory, threads, uptime), the idea being to check the performance of a bot keeping a conversation. Another technology that I used is the Redis Queue, to build a broadcast microservice using FastAPI.

I also made a CI/CD to run our tests and deploy the code using Github Actions, so all pull requests could only be merged if all tests passed ;)

---

### – TSMX

| Title | Start | End |
| --- | --- | --- |
| Python Dev | 08/2019 | 03/2020 | 

I worked at TSMX developing solutions for the management system for internet providers. I created a solution to optimize the generation of large pdf reports, I also implemented integration with [Cielo](https://desenvolvedores.cielo.com.br/api-portal/en/content/api-ecommerce) and [GalaxPay](https://www.galaxpay.com.br/) to build a payment solution that allows simple transactions and recurring payments (the major request from the clients). Another contribution was to implement a feature to generate Nota Fiscal ([an official document that proves the existence of a commercial act](https://thebrazilbusiness.com/article/complete-guide-to-issue-nota-fiscal-in-brazil)). This solution was based on the original lib [PyTrustNFe](https://github.com/gabicavalcante/PyTrustNFe) with my additional support to my State Government rules.

**Technologies**: Python, Flask Framework, Django, Postgres, Pytest.

---

### – Surfmappers

| Title | Start | End |
| --- | --- | --- |
| Back-end Python Dev | 01/2019 | 07/2019 | 

[Surfmappers](https://www.surfmappers.com/surfer/p/albums) is a marketplace for surf photos, a platform to help photographers to sell surf shots. I provided solutions for the backend, using technologies as Python, Pyramid, Flask and MongoDB. I developed a solution for face recognition to find the athletes faces in the snaps and suggest for them buy it. I used the [MAX-Facial-Recognizer](https://github.com/gabicavalcante/MAX-Facial-Recognizer), a project developed as part of the IBM Code Model Asset Exchange using a model is based on the [FaceNet model](https://github.com/davidsandberg/facenet).

**Technologies**: Python, Flask Framework, Pyramid Framework, Mongo.

---

### – National Education and Research Network (RNP)

| Title | Start | End |
| --- | --- | --- |
| Developer and Researcher | 05/2017 | 05/2019 | 

Federated identity management model provides a solution for credential access proliferation, such as based on passwords. However, it only takes the attacker to find out one password in order to personify the user in all federated service providers. The multi-factor authentication emerge as a solution to increase the authentication process robustness.

In this project, I worked as Developer and Researcher at GT-AMPTo (Multi-Factor Authentication for Everyone) developing a solution for multi-factor authentication to be used on the CAFe Federation. My contribution was build a transposition of such authentication through the physical, allowing Federation Authentication with IoT using [FIDO UAF Standard](https://fidoalliance.org/specifications/) and NFC. The prototype implemented in Python to PN532 reader can be found [here](https://github.com/gabicavalcante/nfc-prototype) and a similar solution to ACS-ACR122U reader is [here](https://github.com/gabicavalcante/ACS-ACR122U).

**Technologies**: Raspberry Pi, Arduino, C/C++, Python, Flask Framework, FIDO and NFC.

---

### – Federal University of Rio Grande do Norte

| Title | Start | End |
| --- | --- | --- |
| Developer and Researcher | 09/2016 | 07/2017 | 

I worked as researcher at [Smart Metropolis Project](http://smartmetropolis.imd.ufrn.br), conducted in the Metropole Digital Institute (IMD) of the Federal University of Rio Grande do Norte (UFRN), in Natal-RN. In this project, I worked on Infrastructure Work Package (WP), and the activities developed by this WP are composed of two work fronts. The first one is related to the development, deployment, and operation of the computational environment (datacenter, servers, cloud, networks, etc.) to enable applications developed within the SmartMetropolis Project to work efficiently.

In turn, the second one refers to the development of an autonomous smart hotspot for Internet access, with capacity to offer connectivity to people and devices in the urban environment. This research was supervised by Prof. Carlos Eduardo da Silva. My work on this project involved security, authentication, authorization.

**Technologies**: Python, Flask Framework, JS, Docker, Git.

---

### – Federal University of Rio Grande do Norte

| Title | Start | End |
| --- | --- | --- |
| Developer and Researcher | 05/2014 | 07/2015 | 

Scientific Initiation Scholarship at the Digital Metropolis Institute (IMD), under orientation of Carlos Eduardo da Silva. I was working on a tool to a Multicriteria Approaches for Cloud Services Selection, to solve the issue of selection of cloud services based on the analysis and use of methods, models and algorithms for selection which meet multiple criteria.

With the visibility that cloud computing has been acquiring, it is observed that the provision of computational resources as services is growing increasingly, leading to a large number of services being offered. These services have heterogeneous managerial and technical specifications, so that organizations wishing to use such services need mechanisms to assist in the decision making process to choose one that best suits their needs.

**Technologies**: Java and RDF.

---

### – Anchor Loans

| Title | Start | End |
| --- | --- | --- |
| Python Developer | 12/2013 | 03/2014 | 

In December/2013 I started to work remotely as an Python Developer Intern at Anchor Loans. I was working on projects includes the internal administrative systems.

**Technologies**: Python, Pyramid Framework, MongoDB.

---

# Education

| School | Year | Type Major |
| --- | --- | --- |
| Université Nice Sophia Antipolis | 2015-2016 | Sandwich Degree (exchange program BRAFITEC), Informatique et Gestion |
| Federal University of Rio Grande do Norte | 2012-2016 | BSc, Information Technology |

# Small Courses

| Course Name | Year | Institution | Certificate |
| --- | --- | --- | --- |
| MongoDB Basics | 2020 | Mongo University | [Link](https://university.mongodb.com/course_completion/c4c38ed7-fe17-4877-a2fc-8c096451b9b8/printable) | 

# Languages

| Language | Level |
| --- | --- |
| Portuguese | Native |
| English | Professional working |
| French | A2 | 

# Talks and Workshops

| Title | Type | Conference | Locality | Date |
| --- | --- | --- | --- | --- |
| [Web Scraping](https://slides.com/gabicavalcante/web-scraping) | Talk | — | — | — |
| What I learned with PyLadies | Talk | 1° PyLadies Brazil Conf | Natal, Brazil | Oct/18 |
| Python: O poder da linguagem, diversidade e mercado de trabalho | Talk | Campus Party Recife 2016 | Natal, Brazil | Aug/16 | 

# Publications

- Multi-Factor Authentication for Shibboleth Identity Providers — Journal of Internet Services and Applications, 2020
- Google COVID-19 Community Mobility Reports: Insights from Multi-Criteria Decision Making
- A Multi-Objective Time Series Analysis of Community Mobility Reduction Comparing First and Second COVID-19 Waves

# Articles

- [Build a Secure Twilio Webhook with Python and FastAPI](https://www.twilio.com/blog/build-secure-twilio-webhook-python-fastapi)
- [Build a Secret Santa Bot for WhatsApp Using Python and Twilio](https://www.twilio.com/blog/build-secret-santa-bot-whatsapp-python-twilio)
- [Build an SMS Microservice Using Python, Twilio and Redis Pub/Sub](https://www.twilio.com/en-us/blog/developers/community/sms-microservice-python-twilio-redis-pub-sub)
- [Python, Django and GitHub CI/CD](https://medium.com/@_gabiCavalcante/python-django-and-github-ci-cd-65f9eae7e6fa)
- [WebScraping, Python e Ordem da Câmara dos Vereadores](https://medium.com/@_gabiCavalcante/webscraping-python-e-ordem-da-c%C3%A2mara-dos-deputados-f6b46a088228)

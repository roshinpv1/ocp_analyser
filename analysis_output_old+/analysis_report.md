# Code Analysis Report for Assays sake kwekjw kejwkje kwjekj wejwkj ew

## Executive Summary

- **Security & Quality Implementation**: 53.3%
- **Practices Implemented**: 8 fully, 0 partially, 7 not implemented
- **Total Findings**: 0
- **Component Declaration Mismatches**: 1

## Intake Form Validation

❌ **Intake form is incomplete.** Some mandatory fields have not been answered or Git repository is invalid.

- Total questions: 83
- Mandatory fields: 83
- Unanswered mandatory fields: 79
- Git repository URL: https://github.com/sherlock-project/sherlock
- Git repository valid: ✅ Yes

### Unanswered Mandatory Questions

- Assays sake kwekjw kejwkje kwjekj wejwkj ew
- Provide the GIT CD repo link and coresponding Prod equivalent branch name
- Is the Prod Version of code running in DEV PCF?
- Provide active Dev env name
- Is the Prod Version of code running in SIT PCF?
- Provide active Sit env name
- Is the Prod Version of code running in UAT PCF?
- Provide active UAT env name
- What is the Dev PCF Foundation/ Org/Space the code is running?
- What is the SIT PCF Foundation/ Org/Space the code is running?
- What is the UAT PCF Foundation/ Org/Space the code is running?
- Note : If you have additional Non Prod env Please mention those.
- What is the target OCP env the app team would like to deploy the Component to? (Sterling / Lewisville / Manassas)
- Provide the AD-ENT groups needed to work on the app? E.g. GIT access, Splunk Access etc.
- Is there any test user that can be used during testing ? (Applicable for Ul app)
- Does the App needs any Vanity URL if so any preference on the URL Please mention.
- To implement Vanity URL, the migration team will need the Venafi CERT and the KEY
- What are the Up stream and down stream app that might get impacted with this component?
- Provide the CMP Link
- Please share us the steps on how to request access to PCF app manager as lead engineer for DEV/SIT/UAT environments
- What is the Performance PCF Foundation/ Org/Space the code is running?
- Is the App currently actively running in PCF?
- Is the component
    1   existing parallelly in GitHub On-Prem and GitHub Cloud,
    2   only existing in GitHub On-Prem,
    3   only existing in GitHub Cloud (Github on-prem repo has been archived already)
- Do we have Smoke test data available?
- Is the application component a Batch(AutoSys) / Ul / API app?
- Is the application component using Bridge Utility Server in PCF?
- Is the application component using Java / net / Python / Angular / React
- What is the current Build Pack (for example -Gradle, Maven, NPM etc.) used in this application component
- is component using EPL/EPLX?
- Is the component using Venafi?
- Is the component using Redis?
- Is the component using Channel Secure / PingFed?
- Is the component using NAS / SMB?
- If this component is using NAS/SMB, does app team have the AD-ENT or QA-ENT credentials to configure the same for volume mounts in OCP?
- If this component is not using NAS/SMB, please ignore this question?
- Is the component using SMTP?
- Is the component using AutoSys?
Is the component using CRON/quartz/spring batch or any other batch operation?
- Is the component using MTLS / Mutual Auth Or hard rock pattem in the application?
- Is the component using NDM?
- Is the component using legacy JKS file?
- Is the component using SOAP Calls?
- Is the component using REST API?
- Is the component using APIGEE?
- Is the component using KAFKA?
- Is the component using IBM MQ?
- If the compoenent is using MQ, Is the component using any Cipher suite?
- If the component is not using MQ, ignore this line item?
- Is the component using LDAP?
- Is the Component using Splunk?
- Is the Component using AppD?
- Is the Component using ELASTIC APM?
- Is the component using Hamess or UCD for CI CD
- Is the component storing secure values in Hashicorp vault Or any other external secure credential storage.
Please share the details of where the secure properties are stored?
- Is the compone t using Bridge Utility server in PCF?
- Is the Component using hardRock / MTLS auth?
- Is the Component using AppDynamics?
- Is the Component using RabbitMQ
- Is the component using Database?
- Is the component using MongoDB?
- Is the component using SQLServer?
- Is the component using MySQL?
- Is the component using PostgreSQL?
- Is the component using PostgreSQL?
- Is the component using Oracle?
- Is the component using Cassandra?
- Is the component using Couchbase?
- Is the component using Neo4j?
- Is the component using Hadoop?
- Is the component using Spark?
- Is the component using Okta?
- Is the component using SAML?
- Is the component using Auth?
- Is the component using JWT?
- Is the component using OpenID?
- Is the component using ADFS?
- Is the component using SAN?
- Is the component using MalwareScanner?
- Is the component using any other service? Please share details of the same.
- Are there any application URLs hardcoded in application code or property files?
If Yes, Please share details on the same.

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Intake Form Validation](#intake-form-validation)
3. [Component Analysis](#component-analysis)
4. [Security and Quality Practices](#security-and-quality-practices)
5. [Technology Stack](#technology-stack)
7. [Action Items](#action-items)

## Component Analysis

The following table compares the components declared in the intake form with the components detected in the codebase:

| Component | Declared | Detected | Status |
|-----------|----------|----------|--------|
| venafi | No | No | Match |
| redis | No | No | Match |
| channel secure / pingfed | No | No | Match |
| nas / smb | No | No | Match |
| smtp | No | No | Match |
| autosys | No | No | Match |
| mtls / mutual auth or hard rock pattem in the application | No | No | Match |
| ndm | No | No | Match |
| legacy jks file | No | No | Match |
| soap calls | No | No | Match |
| rest api | No | No | Match |
| apigee | No | No | Match |
| kafka | No | No | Match |
| ibm mq | No | No | Match |
| mq, is the component using any cipher suite | No | No | Match |
| ldap | No | No | Match |
| splunk | No | No | Match |
| appd | No | No | Match |
| elastic apm | No | No | Match |
| hamess or ucd for ci cd | No | No | Match |
| hardrock / mtls auth | No | No | Match |
| appdynamics | No | No | Match |
| rabbitmq | No | Yes | Mismatch |
| database | No | No | Match |
| mongodb | No | No | Match |
| sqlserver | No | No | Match |
| mysql | No | No | Match |
| postgresql | No | No | Match |
| oracle | No | No | Match |
| cassandra | No | No | Match |
| couchbase | No | No | Match |
| neo4j | No | No | Match |
| hadoop | No | No | Match |
| spark | No | No | Match |
| okta | No | No | Match |
| saml | No | No | Match |
| auth | No | No | Match |
| jwt | No | No | Match |
| openid | No | No | Match |
| adfs | No | No | Match |
| san | No | No | Match |
| malwarescanner | No | No | Match |
| any other service | No | No | Match |

## Security and Quality Practices

The following sections summarize the security and quality practices implemented in the codebase:

### Auditability

| Practice | Status | Evidence |
|----------|--------|----------|
| Avoid Logging Confidential Data | Implemented | ['sherlock_project/sherlock.py: `def check_for_parameter(username):`', 'sherlock_project/notify.py: `class QueryNotifyPrint(QueryNotify):`'] |
| Create Audit Trail Logs | Not Implemented | [] |
| Tracking Id For Log Messages | Not Implemented | [] |
| Log Rest Api Calls | Implemented | ['.actor/actor.sh: `curl --request POST ...`'] |
| Log Application Messages | Implemented | ['sherlock_project/sherlock.py: `if errorContext:`', 'sherlock_project/notify.py: `class QueryNotifyPrint(QueryNotify):`'] |
| Client Ui Errors Are Logged | Not Implemented | [] |

### Availability

| Practice | Status | Evidence |
|----------|--------|----------|
| Retry Logic | Implemented | ['sherlock_project/sherlock.py: `from requests_futures.sessions import FuturesSession`'] |
| Set Timeouts On Io Operations | Implemented | ['.actor/actor.sh: `timeout: int = 60`'] |
| Throttling Drop Request | Not Implemented | [] |
| Circuit Breakers On Outgoing Requests | Not Implemented | [] |

### Error Handling

| Practice | Status | Evidence |
|----------|--------|----------|
| Log System Errors | Implemented | ['sherlock_project/sherlock.py: `if errorContext:`'] |
| Use Http Standard Error Codes | Not Implemented | [] |
| Include Client Error Tracking | Implemented | ['.actor/actor.sh: `curl --request POST ...`'] |

### Monitoring

| Practice | Status | Evidence |
|----------|--------|----------|
| Url Monitoring | Not Implemented | [] |

### Testing

| Practice | Status | Evidence |
|----------|--------|----------|
| Automated Regression Testing | Implemented | ['.actor/README.md: "Apify Console"'] |

## Technology Stack

The following technologies were identified in the codebase:

### Programming Languages

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| Python | 3.12 | Main application language | Dockerfile, sherlock_project/sherlock.py (+4) |

### Libraries

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| requests | 2.28.1 | HTTP library | sherlock_project/sherlock.py, sherlock_project/notify.py (+1) |
| pandas | 1.5.3 | Data manipulation library | sherlock_project/sherlock.py, sherlock_project/sites.py |
| requests_futures | 2.4.0 | Asynchronous HTTP requests | sherlock_project/sherlock.py |

### Tools

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| Docker | latest | Containerization tool | Dockerfile |
| Apify SDK | unknown | Serverless microservices pl... |  |

### Other

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| colorama | 0.4.1 | ANSI escape sequences for t... | sherlock_project/notify.py |
| apify-client | unknown | Apify client library |  |


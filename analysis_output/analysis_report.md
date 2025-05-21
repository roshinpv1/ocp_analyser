# Code Analysis Report for sherlock

## Intake Form Validation

❌ **Intake form is incomplete.** Some mandatory fields have not been answered.

- Total questions: 163
- Mandatory fields: 65
- Unanswered mandatory fields: 63

### Unanswered Mandatory Questions

- Is the Prod Version of code running in DEV PCF?
- Is the Prod Version of code running in SIT PCF?
- Is the Prod Version of code running in UAT PCF?
- What is the Dev PCF Foundation/ Org/Space the code is running?
- What is the SIT PCF Foundation/ Org/Space the code is running?
- What is the UAT PCF Foundation/ Org/Space the code is running?
- Note : If you have additional Non Prod env Please mention those.
- Provide the CMP Link
- Please share us the steps on how to request access to PCF app manager as lead engineer for DEV/SIT/UAT environments
- Is the application component a Batch(AutoSys) / Ul / API app?
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

## Component Analysis

The following table shows components identified in the codebase:

| Component | Detected | Evidence |
|-----------|----------|----------|
| Apigee | ❌ No | No APigEE components found |
| Appdynamics | ❌ No | No AppDynamics components found |
| Authentication_Methods_Adfs | ❌ No | No ADFS components found |
| Authentication_Methods_Auth | ❌ No | No Auth components found |
| Authentication_Methods_Jwt | ❌ No | No JWT components found |
| Authentication_Methods_Okta | ❌ No | No Okta components found |
| Authentication_Methods_Openid | ✅ Yes | Found OpenID authentication in .actor/input_schema.json and sherlock_project/sherlock.py |
| Authentication_Methods_Saml | ❌ No | No SAML components found |
| Autosys | ❌ No | No AutoSys components found |
| Bridge_Utility_Server | ❌ No | No Bridge Utility server components found |
| Channel_Secure_Pingfed | ❌ No | No Channel Secure / PingFed components found |
| Cron_Quartz_Spring_Batch | ❌ No | No CRON/quartz/spring batch components found |
| Databases_Cassandra | ❌ No | No Cassandra configurations or dependencies found |
| Databases_Couchbase | ✅ Yes | Found Couchbase in sherlock_project/resources/data.json |
| Databases_Hadoop | ❌ No | No Hadoop configurations or dependencies found |
| Databases_Mongodb | ✅ Yes | Found MongoDB in sherlock_project/resources/data.json |
| Databases_Mysql | ✅ Yes | Found MySQL in sherlock_project/resources/data.json |
| Databases_Neo4J | ❌ No | No Neo4j configurations or dependencies found |
| Databases_Oracle | ❌ No | No Oracle configurations or dependencies found |
| Databases_Postgresql | ✅ Yes | Found PostgreSQL in sherlock_project/resources/data.json |
| Databases_Spark | ❌ No | No Spark configurations or dependencies found |
| Databases_Sqlserver | ❌ No | No SQLServer configurations or dependencies found |
| Elastic_Apm | ❌ No | No ELASTIC APM components found |
| Harness_Or_Ucd_For_Ci_Cd | ❌ No | No Harness or UCD for CI/CD components found |
| Hashicorp_Vault | ❌ No | No Hashicorp vault components found |
| Ibm_Mq | ❌ No | No IBM MQ components found |
| Kafka | ❌ No | No KAFKA components found |
| Ldap | ❌ No | No LDAP configurations or dependencies found |
| Legacy_Jks_Files | ❌ No | No legacy JKS files found |
| Mtls_Mutual_Auth_Hard_Rock_Pattern | ❌ No | No MTLS / Mutual Auth / Hard Rock pattern configurations or dependencies found |
| Nas_Smb | ❌ No | No NAS / SMB configurations or dependencies found |
| Ndm | ❌ No | No NDM components found |
| Rabbitmq | ❌ No | No RabbitMQ components found |
| Redis | ❌ No | No Redis dependencies or configurations found |
| Rest_Api | ✅ Yes | Found REST API endpoints in .actor/README.md and .actor/actor.json |
| Smtp | ❌ No | No SMTP configurations or dependencies found |
| Soap_Calls | ❌ No | No SOAP Calls configurations or dependencies found |
| Splunk | ❌ No | No Splunk components found |
| Venafi | ❌ No | No Venafi certificate management in security/certs.py |

## Technology Stack

### Programming Languages

- **Python** (v3.12)
  - Purpose: Main application language for the Sherlock project
  - Files: sherlock_project/sherlock.py, sherlock_project/__init__.py

### Frameworks

- **FuturesSession**
  - Purpose: Asynchronous HTTP request handling in the Sherlock project
  - Files: sherlock_project/sherlock.py

- **Pandas**
  - Purpose: Data manipulation and analysis library for the Sherlock project
  - Files: sherlock_project/__init__.py, sherlock_project/result.py

### Libraries

- **requests_futures**
  - Purpose: Asynchronous HTTP requests library in the Sherlock project
  - Files: sherlock_project/sherlock.py

- **torrequest**
  - Purpose: Tor circuit management in the Sherlock project, now deprecated
  - Files: sherlock_project/sherlock.py

### Databases

- **SQLite**
  - Purpose: In-memory database used by the Sherlock project for caching and storage
  - Files: sherlock_project/__init__.py, sherlock_project/result.py

### Tools

- **Docker** (v3.12-slim-bullseye)
  - Purpose: Containerization for running the Sherlock project
  - Files: Dockerfile

- **Apify SDK**
  - Purpose: Automated testing and data analysis tool used by the Sherlock project
  - Files: .actor/actor.json, .actor/README.md, .actor/actor.sh, .actor/input_schema.json

## Summary

Total findings: 0

## Conclusion

No significant issues were found in the codebase. The code appears to follow good practices in terms of security, reliability, and maintainability.

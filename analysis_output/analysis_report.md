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
| Apigee | ❌ No | No ApigEE components detected |
| Appd_Or_Appdyn | ❌ No | No AppD or AppDynamics components detected |
| Autosys | ❌ No | No AutoSys components detected |
| Bridge_Utility_Server | ❌ No | No Bridge Utility server components detected |
| Channel_Secure_Or_Pingfed | ❌ No | No Channel Secure or PingFed components detected |
| Cron_Quartz_Spring_Batch | ❌ No | No CRON, Quartz, or Spring Batch components detected |
| Elastic_Apm | ❌ No | No Elastic APM components detected |
| Harness_Or_Ucd_For_Ci_Cd | ❌ No | No Harness or UCD for CI/CD components detected |
| Hashicorp_Vault | ❌ No | No Hashicorp vault components detected |
| Ibm_Mq | ❌ No | No IBM MQ components detected |
| Kafka | ❌ No | No Kafka components detected |
| Ldap | ❌ No | No LDAP components detected |
| Legacy_Jks_Files | ❌ No | No legacy JKS files detected |
| Mtls_Or_Mutual_Auth_Hard_Rock_Pattern | ❌ No | No MTLS, Mutual Auth, or Hard Rock pattern components detected |
| Nas_Smb | ❌ No | No NAS or SMB components detected |
| Ndm | ❌ No | No NDM components detected |
| Rabbitmq | ✅ Yes | Found RabbitMQ in .actor/actor.sh and sherlock_project/sherlock.py |
| Redis | ❌ No | No Redis dependencies or configurations found |
| Rest_Api | ✅ Yes | Found REST API calls in .actor/actor.sh and sherlock_project/sherlock.py |
| Smtp | ❌ No | No SMTP components detected |
| Soap_Calls | ❌ No | No SOAP Calls detected |
| Splunk | ❌ No | No Splunk components detected |
| Venafi | ❌ No | No Venafi certificate management in security/certs.py |

## Technology Stack

### Programming Languages

- **Python** (v3.12)
  - Purpose: Main application language
  - Files: sherlock_project/__main__.py, sherlock_project/sherlock.py, sherlock_project/notify.py, sherlock_project/result.py, sherlock_project/sites.py

### Frameworks

- **Requests-futures** (v0.2.2)
  - Purpose: Asynchronous HTTP requests library
  - Files: sherlock_project/__main__.py

### Libraries

- **Pandas** (v1.5.3)
  - Purpose: Data manipulation and analysis tool
  - Files: sherlock_project/result.py, sherlock_project/sites.py

- **Colorama** (v0.4.6)
  - Purpose: Cross-platform colored terminal text
  - Files: sherlock_project/__main__.py

- **APYFuturesSession**
  - Purpose: Custom futures session for requests with response time measurement
  - Files: sherlock_project/sherlock.py

### Databases

- **None**
  - Purpose: No database dependencies or configurations found
  - Files: N/A

### Tools

- **Docker** (vlatest)
  - Purpose: Containerization platform
  - Files: Dockerfile

- **Apify**
  - Purpose: Cloud-based actor platform for serverless microservices
  - Files: .actor/actor.json, .actor/README.md

### Services

- **None**
  - Purpose: No service dependencies or configurations found
  - Files: N/A

## Summary

Total findings: 0

## Conclusion

No significant issues were found in the codebase. The code appears to follow good practices in terms of security, reliability, and maintainability.

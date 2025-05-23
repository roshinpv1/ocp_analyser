# Code Analysis Report for Assays sake kwekjw kejwkje kwjekj wejwkj ew

## Executive Summary

- **Security & Quality Implementation**: 33.3%
- **Practices Implemented**: 5 fully, 0 partially, 10 not implemented
- **Total Findings**: 0
- **Component Declaration Mismatches**: 1

## Intake Form Validation

❌ **Intake form is incomplete.** Some mandatory fields have not been answered or Git repository is invalid.

- Total questions: 83
- Mandatory fields: 38
- Unanswered mandatory fields: 35
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
- If this component is using NAS/SMB, does app team have the AD-ENT or QA-ENT credentials to configure the same for volume mounts in OCP?
- If this component is not using NAS/SMB, please ignore this question?
- If the component is not using MQ, ignore this line item?
- Is the component storing secure values in Hashicorp vault Or any other external secure credential storage.
Please share the details of where the secure properties are stored?
- Is the compone t using Bridge Utility server in PCF?
- Are there any application URLs hardcoded in application code or property files?
If Yes, Please share details on the same.

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Component Analysis](#component-analysis)
3. [Security and Quality Practices](#security-and-quality-practices)
4. [Technology Stack](#technology-stack)
5. [Jira Stories](#jira-stories)
6. [Action Items](#action-items)
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
| rest api | No | Yes | Mismatch |
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
| rabbitmq | No | No | Match |
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
| Avoid Logging Confidential Data | Not Implemented | No evidence of logging confidential data checks |
| Create Audit Trail Logs | Not Implemented | No comprehensive audit trail logs found |
| Tracking Id For Log Messages | Not Implemented | No evidence of tracking IDs in log messages |
| Log Rest Api Calls | Implemented | REST API calls logged within actor.sh |
| Log Application Messages | Not Implemented | No explicit logging of application messages found |
| Client Ui Errors Are Logged | Not Implemented | No evidence of client-side error logging handlers |

### Availability

| Practice | Status | Evidence |
|----------|--------|----------|
| Retry Logic | Implemented | Retry logic implemented in sherlock.py using Fu... |
| Set Timeouts On Io Operations | Implemented | Timeouts set for HTTP requests in sherlock.py u... |
| Throttling Drop Request | Not Implemented | No evidence of throttling or request dropping l... |
| Circuit Breakers On Outgoing Requests | Not Implemented | No evidence of circuit breaker implementation f... |

### Error Handling

| Practice | Status | Evidence |
|----------|--------|----------|
| Log System Errors | Implemented | Error handling and logging implemented in sherl... |
| Use Http Standard Error Codes | Implemented | Standard HTTP status codes used in the API resp... |
| Include Client Error Tracking | Not Implemented | No evidence of client-side error tracking |

### Monitoring

| Practice | Status | Evidence |
|----------|--------|----------|
| Url Monitoring | Not Implemented | No evidence of health check or ping endpoints f... |

### Testing

| Practice | Status | Evidence |
|----------|--------|----------|
| Automated Regression Testing | Not Implemented | No automated tests found in the codebase |

## Technology Stack

The following technologies were identified in the codebase:

### Programming Languages

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| Python | 3.12 | Main application langu... | Dockerfile, devel/site-list.py (+7) |
| Bash | unknown | Scripting for actor au... | .actor/actor.sh |

### Frameworks

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| Argparse | unknown | Command-line interface... | sherlock_project/sherlock.py |

### Libraries

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| requests | unknown | HTTP requests for inte... | sherlock_project/sherlock.py |
| requests_futures | unknown | Asynchronous HTTP requ... | sherlock_project/sherlock.py |
| pandas | unknown | Data manipulation and ... | sherlock_project/sherlock.py |
| colorama | unknown | Cross-platform colored... | sherlock_project/sherlock.py |
| json | unknown | JSON data processing | .actor/README.md |

### Tools

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| Apify | unknown | Serverless microservic... | .actor/README.md |
| Docker | unknown | Containerization of th... | Dockerfile |

### Services

| Technology | Version | Purpose | Files |
|------------|---------|---------|-------|
| GitHub | unknown | Version control and re... | Dockerfile |

## Action Items

### 1. Complete Intake Form (Priority: Critical)

Complete all mandatory questions in the intake form to ensure accurate project configuration.

### 2. Resolve Component Discrepancies (Priority: Medium)

Reconcile mismatches between declared components and what's detected in the code.

### 3. Implement 10 Missing Security Practices (Priority: Medium)

Address security gaps to improve overall application security posture.

## Jira Stories

The following Jira stories are relevant to this project:

### XYZ-101: Implement Jira integration for code analyzer

**Status**: In Progress

**Created**: 2023-05-15T10:30:00.000+0000

**Last Updated**: 2023-05-16T14:45:00.000+0000

**Description**:

As a user, I want to see my relevant Jira stories in the code analysis report so that I can track issues related to my codebase.

**Acceptance Criteria:**
- Fetch stories from Jira API
- Display summary, status, and description
- Show comments and attachments
- Integrate with existing report

**Comments**:

- **John Developer** (2023-05-15T15:22:00.000+0000):
  I've started working on this. Initial API connection is working.

- **Maria Manager** (2023-05-15T16:05:00.000+0000):
  Great! Make sure to handle authentication errors gracefully.

**Attachments**:

- XYZ_design_mockup.png (2422 bytes)

### XYZ-102: Fix broken CSS in report generation

**Status**: To Do

**Created**: 2023-05-17T09:15:00.000+0000

**Last Updated**: 2023-05-17T09:15:00.000+0000

**Description**:

The CSS styles in the generated report are not being applied correctly. The Jira stories section is not displaying images properly.

**Steps to reproduce:**
1. Generate a report with Jira stories
2. Open the HTML report
3. Notice the images are not displayed

### XYZ-100: Set up project structure and dependencies

**Status**: Done

**Created**: 2023-05-10T08:00:00.000+0000

**Last Updated**: 2023-05-12T16:30:00.000+0000

**Description**:

Create the initial project structure with requirements.txt, main.py, and necessary modules.

**Comments**:

- **John Developer** (2023-05-12T15:45:00.000+0000):
  Completed and ready for review.

- **Sarah Reviewer** (2023-05-12T16:30:00.000+0000):
  Looks good! Approved.



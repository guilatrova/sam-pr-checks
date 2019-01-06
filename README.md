# Lambda PR Checks

[FineTune](https://www.finetunelearning.com/) will be holding a development **hackfest** during the month of December/2018 where anybody in the company is welcome to participate. Challenge's goal is to bring some new idea that might benefit the company.

This hackfest project brings a collection of PR checks to be run inside AWS lambda, all of them has the same purpose: **A better assessment and review of Pull Requests**.

## Checks Summary

- [Pull Request Standards](#Pull-Request-Standards)
- [Code Freeze](#Code-Freeze)
- [Coverage and Quality](#Coverage-and-Quality)

---

# Pull Request Standards

We want to have every Pull Request and commit to follow our guidelines: Tag the ticket in both title and commit, so we can better identify where the tasks were done.

It gives you both a summary report and a PR check as well.

# Code Freeze

There are moments where no matter how successful the code/test is, we just don't want to merge new stuff right away, so we can better plan our QA testing or just schedule a proper time for doing it.

Since we use Slack a lot, makes sense to have a quick command for enabling/disabling such moments.

It's possible to use
`/codefreeze status`, `/codefreeze enable`, and `/codefreeze disable` for those.

Doing so will block/pass checks in any open PR.

# Coverage and Quality

It's an integration to validade quality (linters) and tests coverage. It works in two phases:

1. [Generate reports](#Generate-Reports)
2. [Assess reports](#Assess-Reports)

Second step may be triggered in row if a PR is already open when reports are generated.

![Coverage and Quality workflow](docs/coverage-quality-diagram.png)

### Generate Reports

We use CircleCI with [coverage.py](https://github.com/nedbat/coveragepy) to generate a xml report, then we use [diff-cover](https://github.com/Bachmann1234/diff-cover) to generate both coverage and quality reports only for changed lines of code.

HTML reports are saved inside CircleCI as [artifacts](https://circleci.com/docs/2.0/artifacts/) alongside the outputs of such commands.

Those saved outputs are sent to a S3 bucket, to be read/processed in next step. You can see an output example for [coverage](tests/payloads/covdiff.txt) and [quality](tests/payloads/qualitydiff.txt).

Reports are processed and gets saved to DynamoDB for assessing later.

### Assess Reports

When a PR gets updated with new code, reports are retrieven from DynamoDB and gives you a summary report and a PR check as well.

The summary have some links with more details pointing to HTML report stored in CircleCI artifacts.

# Building & Testing

It requires:
* [Python 3.7 installed](https://www.python.org/downloads/)
* [Docker installed](https://www.docker.com/community-edition)
* [Python Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (for unit testing)


## SAM testing

**SAM CLI** is used to emulate both Lambda and API Gateway locally and uses our `template.yaml` to understand how to bootstrap this environment (runtime, where the source code is, etc.).

```bash
export AWS_PROFILE={DESIRED_AWS_ACCOUNT}

sam build

sam local start-api
```

`localhost:3000` will be available for testing your functions

## Unit testing

```bash
# Setup virtualenv
virtualenv -p python3.7 .venv
source .venv/bin/activate

# Install dependencies
pip install -r dev-requirements.txt

# Run it
bin/test
```

# Environment Variables

For correct functionality, it requires a couple environment variables to be set.

| Variable | Description | Function |
|---|---|---|
| **GITHUB_TOKEN** | Token used to update PR status and write comments (aka summaries). Token provided should have permissions for repo and write:discussion. | All |
| **GITHUB_USER** | The username assigned for the GitHubToken user (e.g. guilatrova). It's used to double check when a summary should be whether edited or deleted. | All |
| **DOCS_STANDARD_LINK** | Link to the standards document. It will be added to the Guidelines Report. | Pull Request Standards |
| **BUCKET_NAME** | S3 bucket that will be used to store/read quality/coverage reports | Coverage and Quality |

---

* AWS CLI already configured with at least PowerUser permission
* [Python 3 installed](https://www.python.org/downloads/)


## Packaging and deployment

AWS Lambda Python runtime requires a flat folder with all dependencies including the application. SAM will use `CodeUri` property to know where to look up for both application and dependencies.

Firstly, we need a `S3 bucket` where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
aws s3 mb s3://BUCKET_NAME
```

> Becareful here to avoid messing up the bucket used for storing reports (that uses the BUCKET_NAME variable) with this one used for storing the lambda functions.

## Manual deployment

Next, run the following command to package our Lambda function to S3:

```bash
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket BUCKET_NAME
```

Next, the following command will create a Cloudformation Stack and deploy your SAM resources.

```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name lambda-pr-checks \
    --capabilities CAPABILITY_IAM
```

> **See [Serverless Application Model (SAM) HOWTO Guide](https://github.com/awslabs/serverless-application-model/blob/master/HOWTO.md) for more details in how to get started.**

## Script deployment




## Bringing to the next level

Here are a few ideas that you can use to get more acquainted as to how this overall process works:

* Create an additional API resource (e.g. /hello/{proxy+}) and return the name requested through this new path
* Update unit test to capture that
* Package & Deploy

Next, you can use the following resources to know more about beyond hello world samples and how others structure their Serverless applications:

* [AWS Serverless Application Repository](https://aws.amazon.com/serverless/serverlessrepo/)
* [Chalice Python Serverless framework](https://github.com/aws/chalice)
* Sample Python with 3rd party dependencies, pipenv and Makefile: ``sam init --location https://github.com/aws-samples/cookiecutter-aws-sam-python``

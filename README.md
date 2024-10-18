# Desafio GraphQL: Power2GO

Informações de como configurar AWS CLI e AWS SAM CLI: 
https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html

Necessário ter instalado na sua linha de comando LINUX:

- AWS CLI
- AWS SAM CLI
- Python 3.12

Libs necessárias (Python): 

- boto3

Para fazer o build e deploy desse projeto, vá para a pasta principal e rode os comandos:

`sam build`

`sam validate --lint` - Verifica se o arquivo YAML está correto antes do deploy

`sam deploy --guided` 

E mais uma vez *importante*:

`sam deploy --config-file samconfig.toml` - (Não confirme de upar o changeset ainda)

Para rodar o projeto upando o changeset automaticamente:
`sam build` 
`sam deploy --no-confirm-changeset`

Caso alteração tenha dado errado (Caso ative o rollback): 
`aws cloudformation rollback-stack --stack-name [nome da stack]`  
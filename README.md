# Desafio Técnico

## Dev

### Apresentação da solução
A arquitetura do sistema, que utilizei para implementar o desafio, foi baseada no artigo [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) de Robert C. Martin (Uncle Bob).

Basicamente, o código fica agrupado em camadas isoladas, protegendo assim as regras de negócio e interfaces externas de alterações que poderiam afetar a aplicação como um todo.

Eu separei o código em 3 camadas (sub-diretórios dentro de ./src):

- "service": são as regras da aplicação, e são independentes das interfaces;
- "repository": são as requisições externas de entrada de dados;
- "delivery": é a interface de entrega de dados através de streaming.

Esta metodologia possui várias vantagens, dentre elas, as principais são:

- Independente de banco de dados e API's externas, visto que toda a implementação de requisições externas, fica isolada na camada "repository";
- Independente de UI, de forma que as regras de negócio, que ficam isoladas na camada "service", só são consumidas pela camada "delivery". Podendo ser uma API REST, console ou um web server.

### Implementação
Para a codificação em si eu usei a metodologia TDD ([Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)). Fato esse que me fez gastar muito tempo, porém, por diversas vezes fui "salvo" pelos testes unitários, que detectavam problemas nas diversas alterações que fiz no código.

Dentro do diretório ./src, estão os sub-diretórios relativos ao Clean Architeture, e dentro de cada sub-diretorio está um diretório "tests", com os testes unitários.

## Ops
### Orquestração
A aplicação foi encapsulada em uma imagem docker, utilizando como base um Python 3 Alpine.

Porém, a aplicação depende de um banco de dados Redis (utilizado como cache e streaming) e um banco de dados MySQL.

Além de um Jupyter Notebook para exibição dos dados agregados.

Para integras todos estes 4 módulos (aplicação, Redis, MySQL e Jupyter), foi utilizado o Docker Compose. Bastando rodar o comando ```docker-compose up``` para que todos os módulos subam, respeitando as dependências entre si, e estejam disponíveis para uso.
### Continuous Integration (CI)
Foi criado um pipeline simples, para uso no Gitlab, visando rodar todos os testes unitários a cada commit.

## Rodando a aplicação
Após dar o ```docker-compose up```, estará disponível um servidor Jupyter Notebook rodando localhost na porta 8888.
Acesse então a URL http://localhost:8888/ no browser.

Será solicitada uma senha para logar no Jupyter.

A senha é "password".

Após logar, acesse a pasta "work" e então clique no arquivo "Candlestick.ipynb".

Com o Notebook aberto, clique no botão "Run", ou acesse o menu "Cell > Run All".

Quando o Notebook começar a executar, será solicitado para informar qual tipo de candle você quer ver. Se é o de 1, 5 ou 10 minutos.

Após o tipo de candle, será solicitado qual par de moedas você que ver os candles. O formato é COIN1_COIN2, tipo USDT_BTC.

Será então, apresentado um gráfico inicialmente vazio, e assim que os candles forem chegando através do streaming do Redis, eles serão plotados.

Caso tenha sido inserido algum valor errado, ou simplesmente quer ver o gráfico para outras configurações, clique no botão com o desenho de 2 setas para a direita (>>), ou acesse o menu "Kernel > Restart & Run All".

## Detalhes dos bancos de dados

### Redis
Dos 16 databases que o Redis fornece, eu utilizei 8. Conforme a seguir:
- db 0: Contém todas as moedas retornadas pelo método "returnCurrencies" da API pública. Para uso caso seja necessário listar todas as moedas;
- db 1: Armazena os tickers retornados no método "returnTicker", respeitando a latência da API pública que é de 6 requisições por segundo;
- db 2, 3 e 4: Armazenam, respectivamente, os candles processado de 1, 5 e 10 minutos;
- db 5, 6 e 7: São, respectivamente, os streams de candles de 1, 5 e 10 minutos.

### MySQL

Cada candle processado é salvo na tabela "db.candles".

O servidor MySQL sobe localhost na porta 3306, usuário "user" e senha "password".
# Acorda! — despertador que não deixa você voltar a dormir

App Android (Kotlin + Jetpack Compose). O alarme só para quando você faz uma
tarefa. Depois, ele volta a tocar se você não fizer uma segunda tarefa dentro do
prazo. A partir de 1 hora antes de tocar, não dá para desligar, mudar nem apagar
o alarme.

## Baixar no celular

Abra no navegador do celular:

**https://github.com/Josejunior-unv/axiumL/releases/latest/download/acorda.apk**

Toque no arquivo baixado para instalar. Se o Android pedir, permita "instalar
apps desconhecidos" para o navegador. Versões novas instalam por cima e mantêm
os alarmes.

Toda vez que algo muda em `app-despertador/`, o GitHub Actions
(`.github/workflows/acorda-android.yml`) roda os testes, compila o APK e publica
no link acima.

## Primeiro uso

1. Abra o app e toque em **Proteção incompleta → Resolver**. Ative todos os
   itens essenciais:
   - **Notificações** e **tela cheia**: para a tarefa aparecer sozinha por cima da
     tela de bloqueio.
   - **Alarmes no minuto exato**.
   - **Proteção contra desinstalar e forçar parada**: liga o app como
     administrador do aparelho. Enquanto estiver ligada, o Android desabilita os
     botões "Desinstalar" e "Forçar parada".
   - **Voltar sozinho para a tarefa** ("sobrepor a outros apps"): se você sair
     da tela da tarefa ou apagar a tela, ela volta em 2 segundos.
   - **Sem economia de bateria**: importante em Xiaomi, Samsung e Motorola. Em
     Xiaomi, ative também o "Início automático" do app.
2. Crie um alarme e toque em **Testar**: ele toca em 5 segundos, do mesmo jeito
   que vai tocar de verdade.

## Como funciona

**Para desligar o som**, uma destas tarefas (você escolhe por alarme):

| Tarefa | Como é |
|---|---|
| Resolver contas | 1 a 15 contas (fácil `27 + 38`, média `(17 × 6) + 45`, difícil `(23 × 7) + (36 × 8)`). Errou, vem outra. |
| Digitar frases | Copiar frases inteiras. Não aceita colar. |
| Sacudir o celular | 10 a 300 sacudidas fortes. |
| Andar | 10 a 500 passos, com o sensor de passos (ou o acelerômetro). |
| Escanear um código | O código de barras ou QR que você cadastrou, de algo longe da cama (a pasta de dente no banheiro, o pacote de café na cozinha). |

Enquanto a tarefa não termina, o som não para. O volume do alarme vai para o
máximo e volta ao máximo se você abaixar. Os botões de volume e o botão voltar
não fazem nada na tela da tarefa.

**Para ele não tocar de novo**: depois que o som para, você tem um prazo (1 a 60
min, padrão 10) para fazer uma segunda tarefa, que também é você que define. Se
o prazo acabar sem a tarefa feita, o alarme volta a tocar desde o começo. Dá para
desligar essa parte em cada alarme.

**A trava**: a partir de 1 hora antes de tocar (dá para mudar para 30 min, 1h30,
2 h ou 3 h, mas só fora da trava), o alarme não pode ser desligado, editado nem
apagado. Também não dá para mexer nos ajustes. Ele continua travado durante o
despertar inteiro, até a confirmação.

### O que fecha cada rota de fuga

| Tentativa | O que acontece |
|---|---|
| Desligar o alarme no app | Bloqueado dentro da janela de trava. |
| Desinstalar ou forçar parada | O Android não deixa enquanto a proteção (administrador) estiver ligada. |
| Desligar a proteção nas configurações | Dentro da janela de trava, o alarme toca **na hora**. |
| Atrasar o relógio do celular | A trava e o toque usam o relógio interno, que conta desde que o celular ligou. Mudar a hora não engana. |
| Desligar ou reiniciar o celular | Ao ligar, o alarme é remarcado. Se ele passou com o celular desligado (até 3 h), toca assim que o celular liga, mesmo antes de digitar a senha. |
| Sair da tela da tarefa ou apagar a tela | A tela volta em 2 segundos (com "sobrepor a outros apps"). |
| Abaixar o volume | Volta para o máximo. |
| O sistema matar o app no meio do toque | Um disparo de reserva religa o som em até 45 s. |

Se a câmera ou o sensor não funcionarem, depois de 3 minutos aparece uma
alternativa: 8 contas difíceis. Assim você não fica preso a um alarme que não
desliga.

### Limites honestos

Nenhum app Android consegue impedir 100% o dono do celular. Dá para fugir
desligando a proteção nas configurações **antes** da janela de trava e depois
desinstalando, ou desligando o celular por mais de 3 horas. O app torna isso
trabalhoso o bastante para não acontecer meio dormindo, que é quando importa.

## Código

```
app-despertador/
├── nucleo/   # Regras em Kotlin puro (calendário, trava, fases, tarefas), com testes
└── app/      # O app Android
    └── src/main/java/br/axiuml/acorda/
        ├── Agenda.kt            # AlarmManager: marca toques, prazos e o vigia
        ├── Fluxo.kt             # Dispara → tarefa → confirmação → acordado (ou toca de novo)
        ├── ToqueService.kt      # Som em loop, volume máximo, vibração, traz a tela de volta
        ├── DespertarActivity.kt # A tela da tarefa, por cima da tela de bloqueio
        ├── Tarefas.kt           # Contas, frases, sacudir, andar, código
        ├── MainActivity.kt      # Lista de alarmes
        ├── Editor.kt            # Criar e editar alarme
        ├── TelaBlindagem.kt     # Permissões e ajustes
        ├── Receptores.kt        # Disparos, boot, mudança de hora, administrador
        └── Armazem.kt           # Onde tudo fica guardado, e a trava
```

Testes das regras (não precisam de Android):

```bash
cd app-despertador
./gradlew :nucleo:test
```

APK (precisa do Android SDK):

```bash
./gradlew :app:assembleRelease
```

A chave que assina o APK (`app/acorda.keystore`) fica no repositório de
propósito: assim toda versão compilada pelo GitHub instala por cima da anterior.
Como o repositório é público, qualquer pessoa poderia assinar um APK com ela.
Instale só pelo link acima.

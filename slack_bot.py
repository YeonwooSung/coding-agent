import os
from concurrent.futures import ThreadPoolExecutor
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import dotenv
import asyncio

dotenv.load_dotenv()

# custom modules
from run_flow import run_flow_from_prompt
from app.logger import logger
from app.constants.slack_bot import (
    THREADPOOL_SIZE,
    RESULT_OK_MSG,
    RESULT_ERROR_MSG,
)
from app.exceptions import LlmCriticalError
from app.dataset.collector import global_collector


_SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
_SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
if not _SLACK_BOT_TOKEN or not _SLACK_APP_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment variables.")


app = App(token=_SLACK_BOT_TOKEN)
executor = ThreadPoolExecutor(max_workers=THREADPOOL_SIZE)


def run_agent(prompt: str):
    """
    에이전트가 실행할 작업을 정의합니다.
    이 함수는 ThreadPool에서 별도 스레드로 실행됩니다.
    """
    logger.info(f"에이전트가 '{prompt}' 명령을 처리 중입니다...")

    # run asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(run_flow_from_prompt(prompt))
        logger.debug(f"에이전트가 '{prompt}' 명령을 처리한 결과: {result}")
        return "✅ 작업이 완료되었습니다."

    except LlmCriticalError as lce:
        logger.error(f"에이전트 실행 중 LLM 오류 발생: {lce}")
        return f"❌ LLM 오류 발생: {str(lce)}"

    except Exception as e:
        logger.error(f"에이전트 실행 중 오류 발생: {str(e)}")
        return f"❌ 에이전트 실행 중 오류 발생: {str(e)}"

    finally:
        loop.close()
        logger.info(f"에이전트가 '{prompt}' 명령 처리를 완료했습니다!")

        # dump collected data
        global_collector.dump(reset=True)


def notify_completion(future, channel_id, thread_ts):
    """
    ThreadPool에서 작업이 완료된 후 호출되는 콜백 함수입니다.
    작업 결과를 슬랙에 알립니다.
    """
    try:
        result = future.result()
        # 작업 완료 메시지 전송
        app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=RESULT_OK_MSG.format(result=result)
        )
    except Exception as e:
        # 오류 발생 시 오류 메시지 전송
        app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=RESULT_ERROR_MSG.format(error=str(e))
        )


# 봇 멘션 이벤트 처리
@app.event("app_mention")
def handle_app_mention(event, say):
    """
    봇이 멘션되었을 때 호출되는 이벤트 핸들러입니다.

    Args:
        event (dict): Slack 이벤트 데이터
        say (function): 메시지를 전송하는 함수
    """
    # 이벤트에서 필요한 정보 추출
    channel_id = event['channel']
    thread_ts = event.get('thread_ts', event['ts'])
    user = event['user']

    # 멘션과 봇 ID를 제외한 실제 명령 텍스트 추출
    # <@BOT_ID> 형식의 멘션 부분을 제거합니다
    text = event['text']
    # 첫 번째 단어(멘션)를 제거
    command_text = ' '.join(text.split()[1:])

    if not command_text:
        say(
            text="명령어를 입력해주세요.",
            thread_ts=thread_ts
        )
        return

    # 작업 시작 메시지 전송
    say(
        text=f"<@{user}> 요청하신 작업을 실행 중입니다...",
        thread_ts=thread_ts
    )

    # ThreadPool에서 에이전트 실행
    future = executor.submit(run_agent, command_text)

    # 작업 완료 알림을 위한 콜백 등록
    future.add_done_callback(
        lambda f: notify_completion(f, channel_id, thread_ts)
    )


# 일반 메시지 이벤트 처리 (경고 없애기 위한 핸들러)
@app.event("message")
def handle_message_events(body, logger):
    """
    일반 메시지 이벤트를 처리합니다. 이 핸들러는 필요에 따라 확장할 수 있습니다.
    """
    # 일반 메시지는 여기서 처리하지 않지만, 경고 메시지를 없애기 위해 핸들러를 등록합니다
    logger.debug(f"메시지 이벤트 감지: {body['event'].get('text', '(no text)')}")


@app.error
def handle_errors(error, body, logger):
    """
    에러 이벤트를 처리합니다.
    """
    logger.error(f"에러 발생: {error}")
    logger.debug(f"에러 발생 시 본문: {body}")

@app.event("app_uninstalled")
def handle_app_uninstalled(event, logger):
    """
    앱이 워크스페이스에서 제거될 때 호출되는 이벤트 핸들러입니다.
    """
    logger.warning("앱이 워크스페이스에서 제거되었습니다. 모든 리소스를 정리합니다.")
    executor.shutdown(wait=False)
    logger.info("ThreadPoolExecutor가 종료되었습니다.")

    global_collector.dump(reset=True)


if __name__ == "__main__":
    logger.info("⚡️ Start up the slack bot...")
    # Socket Mode로 앱 실행
    handler = SocketModeHandler(app, _SLACK_APP_TOKEN)
    handler.start()

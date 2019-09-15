# Ostiarius [![Build Status](https://travis-ci.org/EntryDSM/Ostiarius.svg?branch=master)](https://travis-ci.org/EntryDSM/Ostiarius)

 Ostiarius는 EntryDSM(대덕소프트웨어마이스터고등학교 입학전형시스템)의 MSA 구조 중 게이트웨이 역할을 맡고 있는 웹 애플리케이션 서버입니다. 외부에서 Ostiarius로 요청을 보내면, Ostiarius에서는 이를 역할별로 각각 구분된 마이크로서비스로 요청을 전달합니다. 따라서, 인바운드 규칙 설정을 통해 외부에서는 inter-service로 접근할 수 없고, 오직 Ostiarius를 통해서만 접근할 수 있어 보안적인 측면에서도 유리합니다.

 Production 환경에서는 Docker overlay network를 이용, 보통 3개의 컨테이너가 인바운드 요청을 분산하여 처리하는 구조입니다. 여기서 주의해야 할 점은 Front web client에서는 요청을 보낼 때 HEAD나 OPTIONS를 같이 보내는 경우가 많은데, 이 경우 HEAD와 OPTIONS가 각각 다른 컨테이너로 전송될 수 있어 원활한 응답이 어려울 수 있으니 proxy 설정을 적용해 주는 것이 좋습니다.

## Technical Stacks

- Sanic

## Maintainer

- [SeongHyeon Kim](https://github.com/NovemberOscar)
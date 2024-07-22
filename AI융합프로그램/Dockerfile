FROM conda/miniconda3:latest

RUN rm -rf \
    /usr/lib/x86_64-linux-gnu/libcuda.so* \
    /usr/lib/x86_64-linux-gnu/libnvcuvid.so* \
    /usr/lib/x86_64-linux-gnu/libnvidia-*.so* \
    /usr/lib/firmware \
    /usr/local/cuda/compat/lib

# docker run --gpus all -d -it -v C:\Users\user\Desktop\FLY_AI\FLY_AI_lecture\AI융합프로그램:/root/AI_programming --network=host --name conda skatld802/miniconda3:latest
# docker run -d -it --gpus all --name conda -v C:\Users\user\Desktop\FLY_AI\FLY_AI_lecture\AI융합프 로그램:/root/ai_programming --network=host nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04
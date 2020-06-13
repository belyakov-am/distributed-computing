FROM golang:alpine AS builder

WORKDIR /src/notifications

COPY go.mod .
COPY go.sum .
RUN  go mod download

COPY . .

RUN go build -o /notifications .


FROM alpine

RUN    apk update                                \
    && apk add bash ca-certificates libc6-compat \
    && rm -rf /var/cache/apk/*

COPY --from=builder /notifications ./
package main

import (
	log "github.com/sirupsen/logrus"
	"notifications/config"
	"notifications/mq"
	"notifications/producers"
	"strings"
)

func main() {
	setupLogger()
	cfg := config.ParseEnvConfig()
	log.Info(cfg)
	notifyForever(cfg)
}

func notifyForever(cfg *config.Config) {
	for _, queue := range cfg.Queues {
		var sender *producers.Sender

		if strings.HasPrefix(queue, "email") {
			sender = producers.NewSender(cfg)
		}

		go startManager(queue, sender, cfg)
	}

	forever := make(chan struct{})
	<-forever
}

func startManager(queue string, sender *producers.Sender, cfg *config.Config) {
	manager := mq.NewManager(queue, sender)
	manager.Start(cfg)
}

func setupLogger() {
	log.SetFormatter(
		&log.TextFormatter{
			ForceColors:     true,
			FullTimestamp:   true,
			TimestampFormat: "2006-01-02 15:04:05",
		},
	)
}

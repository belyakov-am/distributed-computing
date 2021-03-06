package mq

import (
	"encoding/json"
	"fmt"
	log "github.com/sirupsen/logrus"
	"github.com/streadway/amqp"
	"notifications/config"
	"notifications/producers"
	"time"
)

type Producer struct {
	queueName string
	channel   *amqp.Channel
}

func NewProducer(queueName string) *Producer {
	return &Producer{
		queueName: queueName,
	}
}

func (producer *Producer) Produce(message *producers.Message) {
	log.Info("[workers.Produce] Producer is trying to return message")

	body, err := json.Marshal(message)
	if err != nil {
		log.WithError(err).Warning("[workers.Produce] JSON marshal failure, message won't be returned to mq")
		return
	}

	queueMessage := amqp.Publishing{
		ContentType: "application/json",
		Body:        []byte(body),
	}

	err = producer.channel.Publish(
		"",
		producer.queueName,
		false,
		false,
		queueMessage,
	)

	log.Info("[workers.Produce] Producer has returned message")

	if err != nil {
		log.WithError(err).Warning("[workers.Produce] Error occurred while returning message")
	}
}

type Consumer struct {
}

func (consumer *Consumer) Consume(queueMessages <-chan amqp.Delivery) *producers.Message {
	queueMessage := <-queueMessages
	body := queueMessage.Body

	var message producers.Message
	err := json.Unmarshal(body, &message)
	if err != nil {
		log.WithError(err).Warning("[workers.Consume] JSON unmarshal failure, skipping message")
	}

	log.WithField("consumed_from", "email_queue").WithTime(time.Now()).Info(message)

	return &message
}

type Manager struct {
	queueName string
	sender    *producers.Sender
	consumer  *Consumer
	producer  *Producer
}

func NewManager(queueName string, sender *producers.Sender) *Manager {
	return &Manager{
		queueName: queueName,
		sender:    sender,
		consumer:  &Consumer{},
		producer:  NewProducer(queueName),
	}
}

func (manager *Manager) Start(cfg *config.Config) {
	log.Print("[workers.Start] Manager is connecting...")

	var connection *amqp.Connection
	dialURL := makeDialURL(cfg)

	for {
		var err error
		connection, err = amqp.Dial(dialURL)
		if err == nil {
			break
		}

		log.WithError(err)
	}
	defer func() { _ = connection.Close() }()

	manager.Work(connection)
}

func (manager *Manager) Work(connection *amqp.Connection) {
	log.Print("[workers.Work] Manager is starting to work")

	channel, err := connection.Channel()
	if err != nil {
		log.WithError(err).Fatal("[workers.Work] Failed to get connection channel")
	}
	defer func() { _ = channel.Close() }()

	manager.producer.channel = channel

	queue, err := channel.QueueDeclare(
		manager.queueName,
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.WithError(err).Fatalf("[workers.Work] Failed to declare mq %v", manager.queueName)
	}

	queueMessages, err := channel.Consume(
		queue.Name,
		"notifications",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.WithError(err).Fatalf("[workers.Work] Failed to consume from %v mq", manager.queueName)
	}

	log.Print("[workers.Work] Manager is starting infinite loop")

	for {
		message := manager.consumer.Consume(queueMessages)
		returnToQueue := manager.sender.Send(message)
		if returnToQueue {
			manager.producer.Produce(message)
		}

		time.Sleep(time.Second / 1)
	}
}

func makeDialURL(cfg *config.Config) string {
	return fmt.Sprintf(
		"amqp://%s:%s@%s:%s",
		cfg.MQUser,
		cfg.MQPassword,
		cfg.MQHost,
		cfg.MQPort,
	)
}

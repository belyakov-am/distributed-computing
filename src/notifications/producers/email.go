package producers

import (
	"crypto/tls"
	"fmt"
	log "github.com/sirupsen/logrus"
	"gopkg.in/gomail.v2"
	"notifications/config"
)

type Message struct {
	Recipient  string  `json:"recipient"`
	Subject    string  `json:"subject"`
	Body       string  `json:"body"`
	RetryCount float64 `json:"retry_count"`
}

type Sender struct {
	dialer *gomail.Dialer
	from   string
}

func (sender *Sender) Send(message *Message) (returnToQueue bool) {
	if message.RetryCount <= 0 {
		log.Info("[email.Send] Email message has reached its send retries limit")
		return false
	}

	message.RetryCount -= 1

	log.WithField("retry_count", fmt.Sprintf("%v->%v", message.RetryCount+1, message.RetryCount)).Info("Email message `retry_count` was decreased")

	mailMessage := newEmailMessage(sender.from, message)
	err := sender.dialer.DialAndSend(mailMessage)
	log.Info("[email.Send] Message sent")

	returnToQueue = err != nil
	if returnToQueue {
		log.WithError(err).Warning("[email.Send] Error occurred while sending")
	}

	return
}

func NewSender(config *config.Config) *Sender {
	sender := &Sender{
		dialer: gomail.NewDialer(
			config.MailHost,
			config.MailPort,
			config.MailSenderEmail,
			config.MailSenderPassword,
		),
		from: config.MailSenderEmail,
	}

	sender.dialer.TLSConfig = &tls.Config{
		InsecureSkipVerify: true,
	}

	return sender
}

func newEmailMessage(from string, message *Message) *gomail.Message {
	mailMessage := gomail.NewMessage()
	mailMessage.SetHeader("From", from)
	mailMessage.SetHeader("To", message.Recipient)
	mailMessage.SetHeader("Subject", message.Subject)
	mailMessage.SetBody("text/html", message.Body)
	return mailMessage
}

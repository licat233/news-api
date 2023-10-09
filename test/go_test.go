package test

import (
	"fmt"
	"testing"
)

type Deed struct {
}

// func (d *Deed) Call() {
// 	fmt.Println("行动")
// }

// func (d *Deed) Ping() {
// 	fmt.Println("Pong Deed")
// }

type Action struct {
}

func (a *Action) Call() {
	fmt.Println("行为")
}

func (a *Action) Ping() {
	fmt.Println("Pong Action")
}

type Person struct {
	*Action
	*Deed
	Name string
}

func (p *Person) Call() {
	fmt.Println(p.Name)
}

func (p *Person) Ping() {
	fmt.Println("Pong Person")
}

func Test_Interface(t *testing.T) {
	type A interface {
		Call()
		Ping()
	}
	type B interface {
		Call()
		Ping()
	}
	type Common interface {
		A
		B
		Call()
		Ping()
	}

	var _ Common = (*Person)(nil)

	var run = func(c Common) {
		c.Ping()
	}

	p := &Person{
		Name:   "张三",
		Action: &Action{},
		Deed:   &Deed{},
	}

	run(p)
}

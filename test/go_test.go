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

type Animal struct {
}

func (a *Animal) Call() {
	fmt.Println("旺旺")
}

func (a *Animal) Ping() {
	fmt.Println("Pong Animal")
}

type Person struct {
	*Animal
}

func (p *Person) Call() {
	fmt.Println("你好")
}

func (p *Person) Ping() {
	fmt.Println("Pong Person")
}

func Test_Interface(t *testing.T) {
	type A interface {
		Call()
		// Ping()
	}
	type B interface {
		Call()
		Ping()
	}
	type Common interface {
		A
		B
		Call()
	}

	var _ Common = (*Person)(nil)

	var run = func(c Common) {
		c.Ping()
	}

	p := &Person{
		Animal: &Animal{},
	}

	run(p)
}

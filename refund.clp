(deftemplate order
   (slot id)
   (slot customer)
   (slot status)
   (slot payment)
   (slot return_period)
   (slot amount)
)

(deftemplate customer
   (slot id)
   (slot type)
)

(defrule full-refund
   (order (id ?orderId) (status delivered) (payment online) (return_period within) (amount ?amt))
   =>
   (printout t "Order " ?orderId " is eligible for a FULL refund of $" ?amt "." crlf)
)

(defrule partial-refund
   (order (id ?orderId) (status returned) (payment online) (return_period within) (amount ?amt))
   =>
   (bind ?refund (* ?amt 0.50))
   (printout t "Order " ?orderId " is eligible for a PARTIAL refund of $" ?refund "." crlf)
)

(defrule escalate-refund
   (order (id ?orderId) (status returned) (amount ?amt))
   (test (> ?amt 500))
   =>
   (printout t "Order " ?orderId " refund ($" ?amt ") requires MANAGER APPROVAL!" crlf)
)
